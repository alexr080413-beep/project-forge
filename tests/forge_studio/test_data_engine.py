from project_forge.forge_studio.data_engine import create_mock_exercise_store


def test_exercise_store_calculates_statistics_from_shared_state() -> None:
    store = create_mock_exercise_store()

    statistics = store.statistics()

    assert statistics["open_injects"] == 7
    assert statistics["completed_injects"] == 1
    assert statistics["pending_reviews"] == 3
    assert statistics["controllers_online"] == 6
    assert statistics["products_generated"] == 12
    assert statistics["timeline_events"] == 8
    assert statistics["exercise_duration"] == "10h 00m"


def test_review_approval_updates_review_inject_dashboard_and_audit_state() -> None:
    store = create_mock_exercise_store()

    payload = store.approve_review("review-001")

    approved_review = next(item for item in payload["review_queue"] if item["id"] == "review-001")
    approved_inject = next(item for item in payload["injects"] if item["id"] == "inject-002")
    latest_audit = payload["audit_log"][0]

    assert approved_review["status"] == "approved"
    assert approved_review["decision"] == "approved"
    assert approved_review["reviewed_by"] == "Maj Warren"
    assert approved_inject["status"] == "approved"
    assert approved_inject["approved_by_name"] == "Maj Warren"
    assert payload["metrics"]["pending_reviews"] == 2
    assert latest_audit["action"] == "review.approved"
    assert latest_audit["target"] == "inject:inject-002"
    assert latest_audit["result"] == "approved"
    assert payload["activity"][0]["title"] == "Civilian Protest Approved"


def test_timeline_operation_updates_statistics_activity_and_audit() -> None:
    store = create_mock_exercise_store()

    payload = store.record_timeline_event(
        title="Controller Sync Complete",
        description="EXCON completed a cross-cell synchronization update.",
    )

    assert payload["statistics"]["timeline_events"] == 9
    assert payload["timeline_events"][-1]["title"] == "Controller Sync Complete"
    assert payload["activity"][0]["title"] == "Controller Sync Complete"
    assert payload["audit_log"][0]["action"] == "timeline.event.created"
