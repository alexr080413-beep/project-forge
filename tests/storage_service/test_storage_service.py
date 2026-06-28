from pathlib import Path

import pytest

from project_forge.storage_service import (
    StorageLocation,
    StorageProvider,
    StorageRegistry,
    StorageRequest,
    StorageResult,
    StorageStatus,
    StorageValidator,
    create_default_storage_registry,
    create_sample_output_location,
    create_sample_storage_request,
)


def location(
    root: Path,
    provider_identifier: str = "local",
    location_id: str = "location",
) -> StorageLocation:
    return StorageLocation(
        location_id=location_id,
        provider_identifier=provider_identifier,
        path=str(root),
    )


def provider(root: Path, identifier: str = "local") -> StorageProvider:
    return StorageProvider(
        identifier=identifier,
        name="Local",
        provider_type="local_file_system",
        root_path=str(root),
    )


def test_default_storage_providers_register_successfully() -> None:
    registry = create_default_storage_registry()

    assert [item.identifier for item in registry.list_providers()] == [
        "archive-folder",
        "azure-blob-placeholder",
        "knowledge-base-folder",
        "local-file-system",
        "output-folder",
        "s3-placeholder",
        "sharepoint-placeholder",
        "template-folder",
    ]


def test_storage_providers_can_be_registered(tmp_path: Path) -> None:
    registry = StorageRegistry()
    item = provider(tmp_path)

    registry.register_provider(item)

    assert registry.get_provider("local") is item


def test_local_provider_dry_run_write_succeeds(tmp_path: Path) -> None:
    registry = StorageRegistry(providers=[provider(tmp_path)])
    result = registry.write(
        location(tmp_path),
        "artifact.txt",
        "Notional content.",
        dry_run=True,
        requested_by="EXCON",
    )

    assert result.status is StorageStatus.DRY_RUN
    assert result.message == "dry-run storage write succeeded"
    assert result.metadata["dry_run"] is True
    assert result.audit_log[-1].startswith("dry-run write")
    assert not (tmp_path / "artifact.txt").exists()


def test_local_provider_write_succeeds_when_not_dry_run(tmp_path: Path) -> None:
    registry = StorageRegistry(providers=[provider(tmp_path)])

    result = registry.write(
        location(tmp_path),
        "artifact.txt",
        "Notional content.",
        dry_run=False,
    )

    assert result.status is StorageStatus.SUCCEEDED
    assert (tmp_path / "artifact.txt").read_text(encoding="utf-8") == "Notional content."


def test_items_can_be_listed_from_configured_folder(tmp_path: Path) -> None:
    (tmp_path / "one.txt").write_text("One", encoding="utf-8")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "two.txt").write_text("Two", encoding="utf-8")
    registry = StorageRegistry(providers=[provider(tmp_path)])

    result = registry.list_items(location(tmp_path))

    assert result.status is StorageStatus.SUCCEEDED
    assert [item.relative_path for item in result.items] == [
        "nested/two.txt",
        "one.txt",
    ]
    assert result.items[0].size_bytes > 0


def test_read_metadata_returns_storage_item(tmp_path: Path) -> None:
    (tmp_path / "artifact.txt").write_text("Metadata", encoding="utf-8")
    registry = StorageRegistry(providers=[provider(tmp_path)])

    result = registry.read_metadata(location(tmp_path), "artifact.txt")

    assert result.status is StorageStatus.SUCCEEDED
    assert result.item is not None
    assert result.item.relative_path == "artifact.txt"
    assert result.item.size_bytes == len("Metadata")


def test_archive_item_dry_run_succeeds(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    archive_dir = tmp_path / "archive"
    source_dir.mkdir()
    archive_dir.mkdir()
    (source_dir / "artifact.txt").write_text("Archive me", encoding="utf-8")
    registry = StorageRegistry(providers=[provider(source_dir)])

    result = registry.archive_item(
        location(source_dir),
        "artifact.txt",
        StorageLocation(
            location_id="archive",
            provider_identifier="local",
            path=str(archive_dir),
        ),
        dry_run=True,
    )

    assert result.status is StorageStatus.DRY_RUN
    assert result.message == "dry-run storage archive succeeded"
    assert not (archive_dir / "artifact.txt").exists()


def test_archive_item_writes_when_not_dry_run(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    archive_dir = tmp_path / "archive"
    source_dir.mkdir()
    archive_dir.mkdir()
    (source_dir / "artifact.txt").write_text("Archive me", encoding="utf-8")
    registry = StorageRegistry(providers=[provider(source_dir)])

    result = registry.archive_item(
        location(source_dir),
        "artifact.txt",
        StorageLocation(
            location_id="archive",
            provider_identifier="local",
            path=str(archive_dir),
        ),
        dry_run=False,
    )

    assert result.status is StorageStatus.SUCCEEDED
    assert (archive_dir / "artifact.txt").read_text(encoding="utf-8") == "Archive me"


def test_invalid_provider_path_fails_validation(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        StorageValidator().validate_provider(provider(tmp_path / "missing"))


def test_invalid_relative_path_fails_validation(tmp_path: Path) -> None:
    registry = StorageRegistry(providers=[provider(tmp_path)])

    with pytest.raises(ValueError):
        registry.write(location(tmp_path), "../outside.txt", "bad")


def test_location_outside_provider_root_fails_validation(tmp_path: Path) -> None:
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    registry = StorageRegistry(providers=[provider(root)])

    with pytest.raises(ValueError):
        registry.list_items(location(outside))


def test_missing_item_metadata_fails_validation(tmp_path: Path) -> None:
    registry = StorageRegistry(providers=[provider(tmp_path)])

    with pytest.raises(FileNotFoundError):
        registry.read_metadata(location(tmp_path), "missing.txt")


def test_placeholder_provider_returns_placeholder_when_not_dry_run() -> None:
    registry = create_default_storage_registry()
    request = StorageRequest(
        request_id="request",
        operation="write",
        location=StorageLocation(
            location_id="s3",
            provider_identifier="s3-placeholder",
            path="s3://project-forge",
        ),
        relative_path="artifact.txt",
        content="No network.",
        dry_run=False,
    )

    result = registry.execute(request)

    assert result.status is StorageStatus.PLACEHOLDER
    assert "no external action performed" in result.message


def test_sample_storage_request_dry_run_succeeds() -> None:
    registry = create_default_storage_registry()

    result = registry.execute(create_sample_storage_request())

    assert result.status is StorageStatus.DRY_RUN
    assert result.metadata["provider_type"] == "output_folder"


def test_sample_output_location_uses_output_folder() -> None:
    assert create_sample_output_location().provider_identifier == "output-folder"


def test_duplicate_providers_are_rejected(tmp_path: Path) -> None:
    item = provider(tmp_path)

    with pytest.raises(ValueError):
        StorageRegistry(providers=[item, item])


def test_validator_requires_audit_metadata() -> None:
    with pytest.raises(ValueError):
        StorageValidator().validate_result(
            StorageResult(
                request_id="request",
                provider_identifier="provider",
                status=StorageStatus.SUCCEEDED,
                operation="list",
                audit_log=[],
            )
        )
