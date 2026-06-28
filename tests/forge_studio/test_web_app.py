from importlib import resources

from project_forge.forge_studio.mock_data import create_mock_registry
from project_forge.forge_studio.web_app import build_dashboard_payload


def test_mock_dashboard_payload_uses_forge_studio_models() -> None:
    registry = create_mock_registry()

    payload = build_dashboard_payload(registry)

    assert payload["active_exercise"]["name"] == "Mountain Exercise 3-27"
    assert payload["workspace"]["exercise"]["exercise_director"] == "Col Smith"
    assert payload["workspace"]["exercise"]["exercise_control"] == "Bridgeport EXCON"
    assert payload["metrics"]["exercise_status"] == "ACTIVE"
    assert payload["metrics"]["exercise_phase"] == "EXECUTE"
    assert payload["metrics"]["exercise_health"] == "Nominal"
    assert payload["metrics"]["pending_reviews"] == 3
    assert payload["metrics"]["open_injects"] == 7
    assert payload["metrics"]["products_generated"] == 12
    assert payload["metrics"]["timeline_events"] == 8
    assert payload["metrics"]["controller_count"] == 7
    assert [item["title"] for item in payload["timeline_summary"][:3]] == [
        "Exercise Begins",
        "Intel Product Published",
        "Civilian Protest Inject",
    ]
    assert [item["id"] for item in payload["pending_reviews"]] == [
        "review-001",
        "review-002",
        "review-003",
    ]
    assert "Photos" in payload["workspace"]["library_folders"]
    assert payload["workspace"]["products"][0]["title"] == "Intelligence Update 001"


def test_static_web_app_assets_exist() -> None:
    static_root = resources.files("project_forge.forge_studio").joinpath("static")

    assert static_root.joinpath("index.html").is_file()
    assert static_root.joinpath("styles.css").is_file()
    assert static_root.joinpath("app.js").is_file()
