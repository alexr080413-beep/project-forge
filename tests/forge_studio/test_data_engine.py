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


def test_inject_crud_synchronizes_dashboard_review_library_controller_and_audit() -> None:
    store = create_mock_exercise_store()

    created = store.apply_action(
        "inject.create",
        {
            "title": "Route Closure",
            "description": "Controller creates a mountain route closure inject.",
            "assigned_controller": "user-intel-chief",
        },
    )
    created_inject = next(item for item in created["injects"] if item["title"] == "Route Closure")

    assert created["metrics"]["pending_reviews"] == 4
    assert created["metrics"]["products_generated"] == 13
    assert created["metrics"]["timeline_events"] == 9
    assert created["review_queue"][-1]["item_id"] == created_inject["id"]
    assert created["products"][0]["title"] == "Route Closure Packet"
    assert next(
        item for item in created["controllers"] if item["user_id"] == "user-intel-chief"
    )["pending_reviews"] == 1
    assert created["audit_log"][0]["action"] == "inject.created"

    edited = store.apply_action(
        "inject.edit",
        {"inject_id": created_inject["id"], "title": "Route Closure Updated"},
    )

    assert any(item["title"] == "Route Closure Updated" for item in edited["injects"])
    assert edited["products"][0]["title"] == "Route Closure Updated Packet"
    assert edited["audit_log"][0]["action"] == "inject.updated"

    deleted = store.apply_action("inject.delete", {"inject_id": created_inject["id"]})

    assert all(item["id"] != created_inject["id"] for item in deleted["injects"])
    assert deleted["metrics"]["products_generated"] == 12
    assert deleted["audit_log"][0]["action"] == "inject.deleted"


def test_timeline_crud_sorts_events_chronologically_and_audits() -> None:
    store = create_mock_exercise_store()

    created = store.apply_action(
        "timeline.create",
        {"title": "Early Update", "description": "Inserted early event.", "timestamp": "0815"},
    )
    event = next(item for item in created["timeline_events"] if item["title"] == "Early Update")

    edited = store.apply_action(
        "timeline.edit",
        {"event_id": event["id"], "title": "Early Update Revised", "timestamp": "0805"},
    )

    assert [item["title"] for item in edited["timeline_events"][:2]] == [
        "Exercise Begins",
        "Early Update Revised",
    ]
    assert edited["audit_log"][0]["action"] == "timeline.event.updated"

    deleted = store.apply_action("timeline.delete", {"event_id": event["id"]})

    assert all(item["id"] != event["id"] for item in deleted["timeline_events"])
    assert deleted["audit_log"][0]["action"] == "timeline.event.deleted"


def test_exercise_and_product_crud_actions_generate_audit_records() -> None:
    store = create_mock_exercise_store()

    created = store.apply_action("exercise.create", {"name": "Mountain Exercise 3-28"})
    assert created["active_exercise"]["name"] == "Mountain Exercise 3-28"
    assert created["audit_log"][0]["action"] == "exercise.created"

    edited = store.apply_action("exercise.edit", {"name": "Mountain Exercise 3-28A"})
    assert edited["active_exercise"]["name"] == "Mountain Exercise 3-28A"
    assert edited["audit_log"][0]["action"] == "exercise.updated"

    duplicated = store.apply_action("exercise.duplicate", {})
    assert duplicated["active_exercise"]["name"] == "Mountain Exercise 3-28A Copy"

    deleted = store.apply_action("exercise.delete", {})
    assert deleted["active_exercise"]["name"] == "Mountain Exercise 3-27"
    assert deleted["audit_log"][0]["action"] == "exercise.deleted"

    archived_product = store.apply_action(
        "product.archive",
        {"product_id": "product-intel-update-001"},
    )
    product = next(
        item for item in archived_product["products"] if item["id"] == "product-intel-update-001"
    )
    assert product["status"] == "Archived"
    assert archived_product["audit_log"][0]["action"] == "product.archived"

    deleted_product = store.apply_action(
        "product.delete",
        {"product_id": "product-intel-update-001"},
    )
    assert deleted_product["metrics"]["products_generated"] == 11
    assert deleted_product["audit_log"][0]["action"] == "product.deleted"


def test_review_revision_updates_queue_library_and_audit() -> None:
    store = create_mock_exercise_store()

    payload = store.apply_action("review.revision", {"review_id": "review-002"})

    review = next(item for item in payload["review_queue"] if item["id"] == "review-002")
    product = next(item for item in payload["products"] if item["id"] == review["item_id"])

    assert review["status"] == "revision_requested"
    assert product["review_status"] == "Revision Requested"
    assert payload["metrics"]["pending_reviews"] == 2
    assert payload["audit_log"][0]["action"] == "review.revision_requested"


def test_platform_context_includes_organizations_exercises_and_workspaces() -> None:
    store = create_mock_exercise_store()

    payload = store.snapshot()

    assert payload["platform"]["hierarchy"] == [
        "Forge",
        "Organization",
        "Exercise",
        "Workspace",
    ]
    assert payload["platform"]["organization"]["name"] == (
        "Marine Corps Mountain Warfare Training Center"
    )
    assert payload["platform"]["exercise"]["name"] == "Mountain Exercise 3-27"
    assert [item["label"] for item in payload["platform"]["workspaces"]] == [
        "Mission Control",
        "Timeline",
        "Intelligence",
        "Inject Library",
        "Exercise Library",
        "Controllers",
        "Review Queue",
        "Reports",
        "Analytics",
        "Administration",
    ]
    assert [item["name"] for item in payload["organizations"]] == [
        "Marine Corps Mountain Warfare Training Center",
        "Expeditionary Operations Training Group",
        "Marine Corps Warfighting Laboratory",
        "Training and Education Command",
        "Joint Training Environment",
    ]
    assert {item["name"] for item in payload["organization_exercises"]} >= {
        "Mountain Exercise 3-27",
        "Winter Mountain Leaders Course",
        "Mountain Exercise 2-27",
    }


def test_switching_exercise_updates_every_workspace_dataset() -> None:
    store = create_mock_exercise_store()

    switched = store.apply_action(
        "context.switch_exercise",
        {"exercise_id": "winter-mountain-leaders-course"},
    )

    assert switched["active_exercise"]["name"] == "Winter Mountain Leaders Course"
    assert switched["platform"]["organization"]["short_name"] == "MWTC"
    assert switched["workspace"]["exercise"]["name"] == "Winter Mountain Leaders Course"
    assert switched["metrics"]["products_generated"] == 2
    assert switched["metrics"]["timeline_events"] == 1
    assert switched["injects"][0]["exercise_id"] == "winter-mountain-leaders-course"
    assert switched["products"][0]["title"] == "Winter Mountain Leaders Course Control Summary"
    assert switched["controllers"][0]["role"] == "Exercise Director"
    assert switched["review_queue"][0]["exercise_id"] == "winter-mountain-leaders-course"


def test_switching_organization_selects_that_organization_active_exercise() -> None:
    store = create_mock_exercise_store()

    switched = store.apply_action("context.switch_organization", {"organization_id": "eotg"})

    assert switched["platform"]["organization"]["short_name"] == "EOTG"
    assert switched["active_exercise"]["name"] == "ITX 2-27"
    assert [item["name"] for item in switched["organization_exercises"]] == ["ITX 2-27"]
    assert switched["workspace"]["exercise"]["name"] == "ITX 2-27"
