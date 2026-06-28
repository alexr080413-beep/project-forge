from importlib import resources

from project_forge.forge_studio.mock_data import create_mock_registry
from project_forge.forge_studio.web_app import build_dashboard_payload


def test_mock_dashboard_payload_uses_forge_studio_models() -> None:
    registry = create_mock_registry()

    payload = build_dashboard_payload(registry)

    assert payload["active_exercise"]["name"] == "Forge Demo Exercise"
    assert payload["metrics"] == {
        "exercise_status": "active",
        "exercise_phase": "execution",
        "pending_reviews": 2,
        "active_injects": 2,
        "timeline_events": 3,
        "controller_count": 4,
    }
    assert [item["title"] for item in payload["timeline_summary"]] == [
        "Execution Phase Started",
        "Approved Media Query Staged",
        "Logistics Inject Entered Review",
    ]
    assert [item["id"] for item in payload["pending_reviews"]] == [
        "review-001",
        "review-002",
    ]


def test_static_web_app_assets_exist() -> None:
    static_root = resources.files("project_forge.forge_studio").joinpath("static")

    assert static_root.joinpath("index.html").is_file()
    assert static_root.joinpath("styles.css").is_file()
    assert static_root.joinpath("app.js").is_file()
