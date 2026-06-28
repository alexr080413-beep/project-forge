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


def test_atlas_objective_crud_updates_validation_and_knowledge_graph() -> None:
    store = create_mock_exercise_store()

    created = store.apply_action(
        "objective.create",
        {
            "title": "Validate sustainment in restricted terrain.",
            "priority": "High",
            "success_criteria": "Logistics request is processed; Resupply decision is recorded",
            "linked_assets": "inject-007; controller-white",
        },
    )
    objective = next(
        item
        for item in created["designer"]["objectives"]
        if item["title"] == "Validate sustainment in restricted terrain."
    )

    assert objective["priority"] == "High"
    assert any(
        node["name"] == "Validate sustainment in restricted terrain."
        for node in created["knowledge_graph"]["nodes"]
    )
    assert created["audit_log"][0]["action"] == "objective.created"

    edited = store.apply_action(
        "objective.edit",
        {
            "objective_id": objective["id"],
            "title": "Validate cold-weather sustainment.",
            "linked_assets": "inject-007; inject-008; controller-white",
        },
    )

    assert any(
        item["title"] == "Validate cold-weather sustainment."
        for item in edited["designer"]["objectives"]
    )
    assert edited["audit_log"][0]["action"] == "objective.updated"

    deleted = store.apply_action("objective.delete", {"objective_id": objective["id"]})

    assert all(item["id"] != objective["id"] for item in deleted["designer"]["objectives"])
    assert deleted["audit_log"][0]["action"] == "objective.deleted"


def test_atlas_inject_and_controller_edits_update_relationships_live() -> None:
    store = create_mock_exercise_store()
    objective_id = store.snapshot()["designer"]["objectives"][0]["id"]

    created_controller = store.apply_action(
        "controller.create",
        {
            "role": "Logistics Controller",
            "name": "Capt Rivera",
            "task": "Resupply disruption planning",
            "responsibilities": "Fuel; Food; Cold-weather equipment",
            "linked_objectives": objective_id,
        },
    )
    controller = next(
        item
        for item in created_controller["designer"]["controllers"]
        if item["role"] == "Logistics Controller"
    )

    created_inject = store.apply_action(
        "inject.create",
        {
            "title": "Resupply Delay",
            "description": "Convoy delay creates sustainment decision pressure.",
            "assigned_controller": "user-controller",
            "objective_id": objective_id,
            "scheduled_time": "1015",
            "priority": "high",
        },
    )
    inject = next(item for item in created_inject["injects"] if item["title"] == "Resupply Delay")

    assert created_inject["designer"]["relationship_map"]["chain"]
    assert any(
        edge["source"] == f"kg-{objective_id}" and edge["target"] == f"kg-{inject['id']}"
        for edge in created_inject["knowledge_graph"]["edges"]
    )

    edited_controller = store.apply_action(
        "controller.edit",
        {
            "controller_id": controller["id"],
            "task": "Resupply disruption and movement friction",
            "linked_injects": inject["id"],
        },
    )
    updated_controller = next(
        item for item in edited_controller["designer"]["controllers"] if item["id"] == controller["id"]
    )

    assert inject["id"] in updated_controller["linked_injects"]
    assert edited_controller["audit_log"][0]["action"] == "controller.updated"


def test_publish_pipeline_blocks_until_validation_succeeds() -> None:
    store = create_mock_exercise_store()

    blocked = store.apply_action("atlas.publish", {})

    assert blocked["publication"]["summary"]["status"] == "blocked"
    assert blocked["publication"]["version_history"] == []
    assert blocked["audit_log"][0]["action"] == "atlas.publish.blocked"
    assert "review-001 is still awaiting human review." in (
        blocked["publication"]["summary"]["validation"]["blocking_issues"]
    )


def test_publish_pipeline_creates_versioned_package_and_opens_mission_control() -> None:
    store = create_mock_exercise_store()
    for review_id in ("review-001", "review-002", "review-003"):
        store.approve_review(review_id)

    validated = store.apply_action("atlas.validate", {})
    assert validated["active_exercise"]["status"] == "validated"
    assert validated["publication"]["summary"]["status"] == "validated"

    published = store.apply_action("atlas.publish", {})

    assert published["active_exercise"]["status"] == "published"
    assert published["execution"]["state"] == "Not Started"
    assert published["workspace"]["exercise"]["timeline_status"] == "Published to Mission Control"
    assert published["publication"]["summary"]["status"] == "published"
    assert published["publication"]["summary"]["version"] == 1
    assert published["publication"]["version_history"] == [
        {
            "package_id": "mountain-exercise-3-27-version-1",
            "version": 1,
            "published_at": "2027-03-27T09:43:00+00:00",
            "validation_status": "ready",
        }
    ]
    package = published["publication"]["latest_package"]
    assert package["version"] == 1
    assert package["exercise"]["name"] == "Mountain Exercise 3-27"
    assert package["objectives"][0]["title"] == (
        "Exercise command and control in complex mountain terrain."
    )
    assert package["timeline"][0]["title"] == "Exercise Begins"
    assert package["injects"][0]["title"] == "IED Discovery"
    assert package["controllers"][0]["role"] == "Exercise Director"
    assert package["knowledge_graph"]["nodes"]
    assert package["relationships"]
    assert package["validation_summary"]["status"] == "ready"
    assert package["publication_timestamp"] == "2027-03-27T09:43:00+00:00"
    assert package["id"] == "mountain-exercise-3-27-version-1"
    assert published["navigation"]["open_workspace"] == "mission-control"
    assert published["products"][0]["title"] == "Exercise Version 1 Publication Summary"
    assert published["audit_log"][0]["action"] == "atlas.exercise.published"

    republished = store.apply_action("atlas.publish", {})
    assert republished["publication"]["summary"]["version"] == 2
    assert [item["version"] for item in republished["publication"]["version_history"]] == [1, 2]


def test_live_execution_engine_updates_state_metrics_activity_and_audit() -> None:
    store = create_mock_exercise_store()
    for review_id in ("review-001", "review-002", "review-003"):
        store.approve_review(review_id)
    store.apply_action("atlas.publish", {})

    started = store.apply_action("execution.start", {})
    assert started["active_exercise"]["status"] == "executing"
    assert started["execution"]["state"] == "Running"
    assert started["activity"][0]["title"] == "Exercise Started"
    assert started["audit_log"][0]["action"] == "execution.started"

    active_event = store.apply_action("timeline.activate", {"event_id": "timeline-003"})
    event = next(item for item in active_event["timeline_events"] if item["id"] == "timeline-003")
    assert event["execution_status"] == "Active"
    assert active_event["execution"]["active_timeline_events"][0]["id"] == "timeline-003"

    delayed = store.apply_action("timeline.delay", {"event_id": "timeline-004"})
    delayed_event = next(item for item in delayed["timeline_events"] if item["id"] == "timeline-004")
    assert delayed_event["execution_status"] == "Delayed"
    assert delayed["metrics"]["delayed_events"] == 1
    assert delayed["execution"]["execution_alerts"][0] == "Cyber Event delayed."

    completed_event = store.apply_action("timeline.complete", {"event_id": "timeline-003"})
    event = next(
        item for item in completed_event["timeline_events"] if item["id"] == "timeline-003"
    )
    assert event["execution_status"] == "Completed"
    assert completed_event["metrics"]["completed_events"] == 1

    released = store.apply_action("inject.release", {"inject_id": "inject-002"})
    inject = next(item for item in released["injects"] if item["id"] == "inject-002")
    assert inject["execution_status"] == "Released"
    assert released["metrics"]["released_injects"] == 1
    assert released["audit_log"][0]["action"] == "inject.released"

    acknowledged = store.apply_action("inject.acknowledge", {"inject_id": "inject-002"})
    inject = next(item for item in acknowledged["injects"] if item["id"] == "inject-002")
    assert inject["execution_status"] == "Acknowledged"

    completed = store.apply_action("inject.complete_execution", {"inject_id": "inject-002"})
    inject = next(item for item in completed["injects"] if item["id"] == "inject-002")
    assert inject["execution_status"] == "Completed"
    assert inject["status"] == "completed"
    assert completed["activity"][0]["title"] == "Capt Nguyen completed inject"

    controller_update = store.apply_action(
        "controller.status",
        {
            "controller_id": "controller-white",
            "status": "Working",
            "note": "Managing civilian protest execution.",
        },
    )
    controller = next(
        item for item in controller_update["controllers"] if item["id"] == "controller-white"
    )
    assert controller["status"] == "Working"
    assert controller["notes"] == "Managing civilian protest execution."

    paused = store.apply_action("execution.pause", {})
    assert paused["execution"]["state"] == "Paused"
    resumed = store.apply_action("execution.resume", {})
    assert resumed["execution"]["state"] == "Running"
    ended = store.apply_action("execution.end", {})
    assert ended["execution"]["state"] == "Completed"
    archived = store.apply_action("execution.archive", {})
    assert archived["execution"]["state"] == "Archived"


def test_review_approve_and_release_affects_execution_flow() -> None:
    store = create_mock_exercise_store()

    payload = store.apply_action("review.approve_release", {"review_id": "review-001"})

    review = next(item for item in payload["review_queue"] if item["id"] == "review-001")
    inject = next(item for item in payload["injects"] if item["id"] == "inject-002")

    assert review["status"] == "approved"
    assert inject["status"] == "approved"
    assert inject["execution_status"] == "Released"
    assert payload["audit_log"][0]["action"] == "inject.released"


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
        "Exercise Designer",
        "Knowledge Graph",
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


def test_exercise_designer_framework_payload_contains_interactive_planning_data() -> None:
    store = create_mock_exercise_store()

    payload = store.snapshot()
    designer = payload["designer"]

    assert designer["name"] == "Project Atlas"
    assert designer["object_categories"] == [
        "Objectives",
        "Units",
        "Controllers",
        "Injects",
        "Decision Points",
        "Weather Events",
        "Intelligence Updates",
        "Media Events",
        "Observer Checkpoints",
        "Templates",
    ]
    planning_titles = {item["title"] for item in designer["planning_objects"]}
    assert {"Exercise Begins", "Civilian Protest", "GPS Interference"} <= planning_titles
    assert designer["objectives"][0]["title"] == (
        "Exercise command and control in complex mountain terrain."
    )
    assert designer["controllers"][0]["role"] == "Exercise Director"
    assert designer["exercise_properties"]["Exercise Name"] == "Mountain Exercise 3-27"
    assert designer["toolbar"] == ["New Exercise", "Save Draft", "Validate", "Publish", "Export"]
    assert [item["label"] for item in designer["validation"]] == [
        "Objectives complete",
        "Controllers assigned",
        "Timeline conflicts",
        "Missing relationships",
        "Publish readiness",
    ]


def test_exercise_designer_relationship_engine_payload_models_assets_and_links() -> None:
    store = create_mock_exercise_store()

    designer = store.snapshot()["designer"]

    assert designer["asset_types"] == [
        "Objective",
        "Inject",
        "Timeline Event",
        "Controller",
        "Product",
        "Intelligence Update",
        "Weather Event",
        "Media Event",
        "Observer Checkpoint",
        "Observation",
        "AAR Finding",
    ]
    assert designer["relationship_types"] == [
        "supports",
        "triggers",
        "depends_on",
        "assigned_to",
        "produces",
        "reviews",
        "observes",
        "evaluates",
        "follows",
        "conflicts_with",
        "related_to",
    ]
    assert {item["type"] for item in designer["exercise_assets"]} >= {
        "Objective",
        "Inject",
        "Timeline Event",
        "Controller",
        "Product",
        "Observation",
        "AAR Finding",
    }
    assert {
        "source": "objective-command-control",
        "target": "inject-002",
        "type": "supports",
    } in designer["relationships"]
    assert designer["relationship_map"]["chain"][0] == "Mountain Exercise 3-27"
    assert designer["relationship_map"]["chain"][-1] == "AAR Finding"


def test_exercise_designer_relationship_validation_and_item_relationships() -> None:
    store = create_mock_exercise_store()

    designer = store.snapshot()["designer"]
    civilian_protest = next(
        item for item in designer["planning_objects"] if item["title"] == "Civilian Protest"
    )

    assert civilian_protest["linked_objectives"] == [
        "Exercise command and control in complex mountain terrain."
    ]
    assert civilian_protest["assigned_controller"] == "White Cell Controller"
    assert civilian_protest["produced_products"] == []
    assert civilian_protest["validation_warnings"] == ["Assign planned time before publish."]
    assert [item["label"] for item in designer["relationship_validation"]] == [
        "Inject objective links",
        "Controller assignments",
        "Scheduled timeline events",
        "Product source references",
        "AAR traceability",
    ]
    assert {item["state"] for item in designer["relationship_validation"]} == {
        "success",
        "warning",
    }


def test_operational_knowledge_graph_payload_models_nodes_and_edges() -> None:
    store = create_mock_exercise_store()

    graph = store.snapshot()["knowledge_graph"]

    assert graph["name"] == "Forge Operational Knowledge Graph"
    assert graph["node_types"] == [
        "Exercise",
        "Objective",
        "Inject",
        "Timeline Event",
        "Controller",
        "Organization",
        "Unit",
        "Product",
        "Intelligence Update",
        "Weather Event",
        "Media Event",
        "Decision Point",
        "Observation",
        "AAR Finding",
        "Template",
    ]
    assert graph["relationship_types"] == [
        "supports",
        "produces",
        "triggers",
        "depends_on",
        "assigned_to",
        "observes",
        "evaluates",
        "references",
        "related_to",
        "precedes",
        "follows",
        "contains",
        "inherits",
    ]
    assert {"Exercise", "Objective", "Inject", "Timeline Event", "Controller", "Product"} <= {
        node["type"] for node in graph["nodes"]
    }
    assert {
        "source": "kg-objective-command-control",
        "target": "kg-inject-002",
        "type": "supports",
    } in graph["edges"]
    assert {
        "source": "kg-inject-004",
        "target": "kg-timeline-004",
        "type": "triggers",
    } in graph["edges"]


def test_operational_knowledge_graph_includes_inspector_filters_and_navigation() -> None:
    store = create_mock_exercise_store()

    graph = store.snapshot()["knowledge_graph"]
    inject_node = next(node for node in graph["nodes"] if node["id"] == "kg-inject-002")

    assert graph["default_node_id"] == "kg-exercise"
    assert graph["filters"] == [
        "Objectives",
        "Injects",
        "Controllers",
        "Products",
        "Weather",
        "Intelligence",
        "Observations",
        "Timeline Events",
        "AAR Findings",
    ]
    assert graph["filter_map"]["Timeline Events"] == [
        "Timeline Event",
        "Decision Point",
    ]
    assert graph["navigation"] == [
        "Click node",
        "Expand neighbors",
        "Collapse neighbors",
        "Center graph",
        "Filter by asset type",
        "Search",
        "Relationship highlighting",
    ]
    assert "Exercise command and control in complex mountain terrain." in (
        inject_node["connected_assets"]
    )
    assert inject_node["relationship_count"] >= 2
    assert inject_node["exercise"] == "Mountain Exercise 3-27"
