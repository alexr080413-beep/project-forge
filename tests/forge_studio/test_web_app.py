from importlib import resources

from project_forge.forge_studio.data_engine import create_mock_exercise_store
from project_forge.forge_studio.web_app import build_dashboard_payload


def test_mock_dashboard_payload_uses_exercise_data_engine() -> None:
    store = create_mock_exercise_store()

    payload = build_dashboard_payload(store)

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
    assert payload["metrics"]["controller_count"] == 6
    assert [item["title"] for item in payload["timeline_events"][:3]] == [
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
    assert payload["products"][0]["title"] == "Intelligence Update 001"
    assert payload["controllers"][0]["role"] == "Exercise Director"
    assert payload["review_queue"][0]["reviewed_by"] == "Maj Warren"
    assert payload["audit_log"][0]["action"] == "inject.review.submitted"


def test_static_web_app_assets_exist() -> None:
    static_root = resources.files("project_forge.forge_studio").joinpath("static")

    assert static_root.joinpath("index.html").is_file()
    assert static_root.joinpath("styles.css").is_file()
    assert static_root.joinpath("app.js").is_file()
