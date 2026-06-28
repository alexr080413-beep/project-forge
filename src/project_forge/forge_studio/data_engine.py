from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from typing import Any

from .mock_data import create_mock_registry
from .models import (
    AuditLog,
    Exercise,
    ExercisePhase,
    ExerciseStatus,
    Inject,
    InjectPriority,
    InjectStatus,
    InjectType,
    ReviewDecision,
    ReviewItemType,
    StudioReviewItem,
    StudioReviewStatus,
    TimelineEvent,
    TimelineEventType,
)
from .registry import ForgeStudioRegistry


@dataclass(frozen=True, slots=True)
class ExerciseProduct:
    """One product generated or archived inside the active exercise."""

    id: str
    folder: str
    product_type: str
    title: str
    status: str
    version: str
    last_updated: str
    author: str
    review_status: str
    metadata: dict[str, str] = field(default_factory=dict)
    version_history: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class ControllerAssignment:
    """Controller-facing assignment derived from the active exercise."""

    id: str
    role: str
    name: str
    task: str
    status: str
    products_today: int
    pending_reviews: int
    user_id: str = ""
    responsibilities: list[str] = field(default_factory=list)
    linked_objectives: list[str] = field(default_factory=list)
    linked_injects: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class PlanningObjective:
    """Editable Atlas planning objective."""

    id: str
    title: str
    priority: str
    success_criteria: list[str] = field(default_factory=list)
    linked_assets: list[str] = field(default_factory=list)
    status: str = "Draft"


@dataclass(frozen=True, slots=True)
class Organization:
    """One Forge Studio organization that owns exercise workspaces."""

    id: str
    name: str
    short_name: str


@dataclass(slots=True)
class ExerciseWorkspaceContext:
    """Exercise-specific UI state owned by the Exercise Data Engine."""

    products: list[ExerciseProduct]
    controllers: list[ControllerAssignment]
    library_folders: list[str]
    settings: list[dict[str, str]]
    objectives: list[str]
    participating_units: list[str]
    activity: list[dict[str, str]]
    exercise_control: str
    exercise_director_id: str
    training_audience: str
    timeline_status: str
    exercise_health: str
    operational_time: str
    planning_objectives: list[PlanningObjective] = field(default_factory=list)
    inject_objective_links: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class ExerciseStore:
    """Single source of truth for the Forge Studio demo exercise.

    The store keeps the runnable app data-driven without adding persistence or a
    frontend framework. Every page receives a snapshot of this object, and every
    mock operation records an audit entry before returning an updated snapshot.
    """

    registry: ForgeStudioRegistry
    products: list[ExerciseProduct] = field(default_factory=list)
    controllers: list[ControllerAssignment] = field(default_factory=list)
    library_folders: list[str] = field(default_factory=list)
    settings: list[dict[str, str]] = field(default_factory=list)
    objectives: list[str] = field(default_factory=list)
    participating_units: list[str] = field(default_factory=list)
    activity: list[dict[str, str]] = field(default_factory=list)
    exercise_control: str = "Bridgeport EXCON"
    exercise_director_id: str = "user-exdir"
    training_audience: str = "2d Battalion, 8th Marines"
    timeline_status: str = "On Plan"
    exercise_health: str = "Nominal"
    operational_time: str = "0942"
    active_exercise_id: str = ""
    organizations: list[Organization] = field(default_factory=list)
    active_organization_id: str = ""
    exercise_organization_map: dict[str, str] = field(default_factory=dict)
    exercise_workspaces: dict[str, ExerciseWorkspaceContext] = field(default_factory=dict)
    planning_objectives: list[PlanningObjective] = field(default_factory=list)
    inject_objective_links: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.organizations:
            self.organizations = _default_organizations()
        if not self.active_organization_id:
            self.active_organization_id = self.organizations[0].id
        if not self.exercise_organization_map:
            self.exercise_organization_map = {
                exercise.id: self.active_organization_id
                for exercise in self.registry.list_exercises()
            }
        if not self.active_exercise_id:
            self.active_exercise_id = self._first_exercise_for_organization(
                self.active_organization_id
            )
        if self.active_exercise_id:
            if self.active_exercise_id not in self.exercise_workspaces:
                self._store_active_workspace_context()
            self._load_workspace_context(self.active_exercise_id)

    @property
    def exercise_id(self) -> str:
        exercise = self._active_exercise()
        if exercise is None:
            raise ValueError("exercise store requires one active exercise")
        return exercise.id

    def snapshot(self) -> dict[str, Any]:
        """Return one JSON-ready exercise state for every application page."""

        exercise = self._required_active_exercise()
        organization = self._required_active_organization()
        statistics = self.statistics()
        exercise_workspace = {
            "id": exercise.id,
            "name": exercise.name,
            "status": exercise.status.value.upper(),
            "phase": (
                "EXECUTE"
                if exercise.phase.value == "execution"
                else exercise.phase.value.upper()
            ),
            "start": _time_label(exercise.start_date),
            "exercise_director": self._user_name(self.exercise_director_id),
            "exercise_control": self.exercise_control,
            "health": self.exercise_health,
            "operational_time": self.operational_time,
            "training_audience": self.training_audience,
            "timeline_status": self.timeline_status,
            "objectives": list(self.objectives),
            "participating_units": list(self.participating_units),
            "statistics": [
                {"label": "Open Injects", "value": str(statistics["open_injects"])},
                {"label": "Completed Injects", "value": str(statistics["completed_injects"])},
                {"label": "Pending Reviews", "value": str(statistics["pending_reviews"])},
                {"label": "Products", "value": str(statistics["products_generated"])},
                {"label": "Timeline Events", "value": str(statistics["timeline_events"])},
                {"label": "Exercise Duration", "value": statistics["exercise_duration"]},
            ],
        }

        timeline_events = self.registry.list_timeline_events(exercise.id)
        review_items = self.registry.list_review_items(exercise.id)
        injects = self.registry.list_injects(exercise.id)
        audit_logs = self.registry.list_audit_logs(exercise.id)
        pending_statuses = {StudioReviewStatus.PENDING, StudioReviewStatus.IN_REVIEW}

        return {
            "platform": {
                "product": "Forge",
                "application": "Forge Studio",
                "hierarchy": ["Forge", "Organization", "Exercise", "Workspace"],
                "organization": _to_jsonable(organization),
                "exercise": {
                    "id": exercise.id,
                    "name": exercise.name,
                    "status": exercise.status.value,
                    "phase": exercise.phase.value,
                },
                "workspace": "Mission Control",
                "breadcrumbs": [
                    {"label": "Forge", "id": "forge"},
                    {"label": organization.short_name, "id": organization.id},
                    {"label": exercise.name, "id": exercise.id},
                    {"label": "Mission Control", "id": "mission-control"},
                ],
                "workspaces": _workspace_definitions(),
            },
            "organizations": [_to_jsonable(item) for item in self.organizations],
            "organization_exercises": [
                _to_jsonable(item) for item in self._exercises_for_active_organization()
            ],
            "active_exercise": _to_jsonable(exercise),
            "exercises": [_to_jsonable(item) for item in self.registry.list_exercises()],
            "workspace": {
                "exercise": exercise_workspace,
                "library_folders": list(self.library_folders),
                "settings": list(self.settings),
            },
            "metrics": {
                "exercise_status": exercise_workspace["status"],
                "exercise_phase": exercise_workspace["phase"],
                "exercise_health": self.exercise_health,
                "current_operational_time": self.operational_time,
                "pending_reviews": statistics["pending_reviews"],
                "open_injects": statistics["open_injects"],
                "completed_injects": statistics["completed_injects"],
                "products_generated": statistics["products_generated"],
                "timeline_events": statistics["timeline_events"],
                "controller_count": statistics["controllers_online"],
                "exercise_duration": statistics["exercise_duration"],
            },
            "activity": list(self.activity),
            "timeline_summary": [_to_jsonable(event) for event in timeline_events],
            "timeline_events": [_to_jsonable(event) for event in timeline_events],
            "pending_reviews": [
                self._review_payload(item)
                for item in review_items
                if item.status in pending_statuses
            ],
            "review_queue": [self._review_payload(item) for item in review_items],
            "injects": [self._inject_payload(item) for item in injects],
            "active_injects": [
                self._inject_payload(item)
                for item in injects
                if item.status is not InjectStatus.COMPLETED
            ],
            "products": [_to_jsonable(product) for product in self.products],
            "controllers": [
                self._controller_payload(controller) for controller in self.controllers
            ],
            "audit_log": [self._audit_payload(log) for log in reversed(audit_logs)],
            "statistics": statistics,
            "search_results": self._mock_search_results(),
            "designer": self._designer_payload(exercise, exercise_workspace),
            "knowledge_graph": self._knowledge_graph_payload(
                exercise,
                organization,
                exercise_workspace,
            ),
        }

    def statistics(self) -> dict[str, Any]:
        """Calculate exercise statistics directly from shared state."""

        exercise = self._required_active_exercise()
        injects = self.registry.list_injects(exercise.id)
        review_items = self.registry.list_review_items(exercise.id)
        pending_statuses = {StudioReviewStatus.PENDING, StudioReviewStatus.IN_REVIEW}
        open_statuses = {
            InjectStatus.DRAFT,
            InjectStatus.PENDING_REVIEW,
            InjectStatus.APPROVED,
            InjectStatus.SCHEDULED,
        }

        return {
            "open_injects": sum(item.status in open_statuses for item in injects),
            "completed_injects": sum(item.status is InjectStatus.COMPLETED for item in injects),
            "pending_reviews": sum(item.status in pending_statuses for item in review_items),
            "controllers_online": sum(item.status == "Online" for item in self.controllers),
            "products_generated": len(self.products),
            "timeline_events": len(self.registry.list_timeline_events(exercise.id)),
            "exercise_duration": _duration_label(exercise.start_date, exercise.end_date),
        }

    def approve_review(self, review_id: str, reviewer_id: str = "user-reviewer") -> dict[str, Any]:
        item = self.registry.approve_review_item(
            review_id,
            reviewer_id,
            comments="Approved through Forge Studio mock review workflow.",
        )
        self._record_operation(
            actor_id=reviewer_id,
            action="review.approved",
            target_type=item.item_type.value,
            target_id=item.item_id,
            result=ReviewDecision.APPROVED.value,
            activity_title=f"{self._item_title(item.item_id)} Approved",
        )
        self._sync_product_review_status(item.item_id, "Approved")
        return self.snapshot()

    def reject_review(self, review_id: str, reviewer_id: str = "user-reviewer") -> dict[str, Any]:
        item = self.registry.reject_review_item(
            review_id,
            reviewer_id,
            comments="Rejected through Forge Studio mock review workflow.",
        )
        self._record_operation(
            actor_id=reviewer_id,
            action="review.rejected",
            target_type=item.item_type.value,
            target_id=item.item_id,
            result=ReviewDecision.REJECTED.value,
            activity_title=f"{self._item_title(item.item_id)} Rejected",
        )
        self._sync_product_review_status(item.item_id, "Rejected")
        return self.snapshot()

    def return_review_for_revision(
        self,
        review_id: str,
        reviewer_id: str = "user-reviewer",
    ) -> dict[str, Any]:
        item = self._required_review(review_id)
        item.record_decision(
            ReviewDecision.REVISION_REQUESTED,
            reviewer_id,
            comments="Returned for revision through Forge Studio mock review workflow.",
        )
        self._sync_product_review_status(item.item_id, "Revision Requested")
        self._record_operation(
            actor_id=reviewer_id,
            action="review.revision_requested",
            target_type=item.item_type.value,
            target_id=item.item_id,
            result=ReviewDecision.REVISION_REQUESTED.value,
            activity_title=f"{self._item_title(item.item_id)} Returned for Revision",
        )
        return self.snapshot()

    def apply_action(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Apply one UI command and return a synchronized exercise snapshot."""

        actions = {
            "exercise.create": self.create_exercise,
            "exercise.edit": self.edit_exercise,
            "exercise.archive": self.archive_exercise,
            "exercise.duplicate": self.duplicate_exercise,
            "exercise.delete": self.delete_exercise,
            "inject.create": self.create_inject,
            "inject.edit": self.edit_inject,
            "inject.delete": self.delete_inject,
            "inject.approve": self.approve_inject,
            "inject.reject": self.reject_inject,
            "inject.assign": self.assign_inject_controller,
            "inject.schedule": self.schedule_inject,
            "timeline.create": self.create_timeline_event,
            "timeline.edit": self.edit_timeline_event,
            "timeline.move": self.edit_timeline_event,
            "timeline.delete": self.delete_timeline_event,
            "objective.create": self.create_objective,
            "objective.edit": self.edit_objective,
            "objective.delete": self.delete_objective,
            "controller.create": self.create_controller,
            "controller.edit": self.edit_controller,
            "atlas.save_draft": self.save_atlas_draft,
            "atlas.validate": self.validate_atlas_plan,
            "atlas.publish": self.publish_atlas_plan,
            "atlas.export": self.export_atlas_plan,
            "review.approve": lambda data: self.approve_review(_required(data, "review_id")),
            "review.reject": lambda data: self.reject_review(_required(data, "review_id")),
            "review.revision": lambda data: self.return_review_for_revision(
                _required(data, "review_id")
            ),
            "product.open": self.open_product,
            "product.metadata": self.view_product_metadata,
            "product.version_history": self.view_product_version_history,
            "product.archive": self.archive_product,
            "product.delete": self.delete_product,
            "context.switch_organization": self.switch_organization,
            "context.switch_exercise": self.switch_exercise,
        }
        if action not in actions:
            raise ValueError(f"unsupported action: {action}")
        return actions[action](payload)

    def switch_organization(self, payload: dict[str, Any]) -> dict[str, Any]:
        organization_id = _required(payload, "organization_id")
        if not any(item.id == organization_id for item in self.organizations):
            raise ValueError(f"organization not found: {organization_id}")
        self._store_active_workspace_context()
        self.active_organization_id = organization_id
        self.active_exercise_id = self._first_exercise_for_organization(organization_id)
        self._load_workspace_context(self.active_exercise_id)
        return self.snapshot()

    def switch_exercise(self, payload: dict[str, Any]) -> dict[str, Any]:
        exercise_id = _required(payload, "exercise_id")
        exercise = self.registry.get_exercise(exercise_id)
        if exercise is None:
            raise ValueError(f"exercise not found: {exercise_id}")
        organization_id = self.exercise_organization_map.get(exercise_id)
        if organization_id:
            self.active_organization_id = organization_id
        self._store_active_workspace_context()
        self.active_exercise_id = exercise.id
        self._load_workspace_context(exercise.id)
        return self.snapshot()

    def create_exercise(self, payload: dict[str, Any]) -> dict[str, Any]:
        name = str(payload.get("name") or "New Exercise").strip()
        exercise = Exercise(
            id=_unique_id(_slug(name), [item.id for item in self.registry.exercises]),
            name=name,
            description=str(payload.get("description") or "Created in Forge Studio."),
            status=ExerciseStatus.ACTIVE,
            phase=ExercisePhase.EXECUTION,
            start_date=_parse_datetime(payload.get("start_date")) or _operation_timestamp(),
            end_date=_parse_datetime(payload.get("end_date")),
        )
        self.registry.register_exercise(exercise)
        self.exercise_organization_map[exercise.id] = self.active_organization_id
        self.active_exercise_id = exercise.id
        self._load_workspace_context(exercise.id)
        self._record_operation(
            actor_id="user-exdir",
            action="exercise.created",
            target_type="exercise",
            target_id=exercise.id,
            result="created",
            activity_title=f"{exercise.name} Created",
        )
        return self.snapshot()

    def edit_exercise(self, payload: dict[str, Any]) -> dict[str, Any]:
        exercise = self._required_active_exercise()
        if payload.get("name"):
            exercise.name = str(payload["name"]).strip()
        if payload.get("description"):
            exercise.description = str(payload["description"]).strip()
        if payload.get("phase"):
            exercise.phase = _enum_value(ExercisePhase, str(payload["phase"]))
        if payload.get("status"):
            exercise.status = _enum_value(ExerciseStatus, str(payload["status"]))
        if payload.get("start_date"):
            exercise.start_date = _parse_datetime(payload.get("start_date"))
        if payload.get("end_date"):
            exercise.end_date = _parse_datetime(payload.get("end_date"))
        if payload.get("exercise_control"):
            self.exercise_control = str(payload["exercise_control"]).strip()
        if payload.get("training_audience"):
            self.training_audience = str(payload["training_audience"]).strip()
        if payload.get("exercise_director_id"):
            self.exercise_director_id = str(payload["exercise_director_id"]).strip()
        exercise.updated_at = _operation_timestamp()
        self._record_operation(
            actor_id="user-exdir",
            action="exercise.updated",
            target_type="exercise",
            target_id=exercise.id,
            result="updated",
            activity_title=f"{exercise.name} Updated",
        )
        return self.snapshot()

    def archive_exercise(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        exercise = self._required_active_exercise()
        exercise.transition_status(ExerciseStatus.ARCHIVED)
        self._record_operation(
            actor_id="user-exdir",
            action="exercise.archived",
            target_type="exercise",
            target_id=exercise.id,
            result="archived",
            activity_title=f"{exercise.name} Archived",
        )
        return self.snapshot()

    def duplicate_exercise(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        source = self._required_active_exercise()
        duplicate = Exercise(
            id=_unique_id(f"{source.id}-copy", [item.id for item in self.registry.exercises]),
            name=f"{source.name} Copy",
            description=source.description,
            status=ExerciseStatus.DRAFT,
            phase=source.phase,
            start_date=source.start_date,
            end_date=source.end_date,
        )
        self.registry.register_exercise(duplicate)
        self.exercise_organization_map[duplicate.id] = self.active_organization_id
        self.active_exercise_id = duplicate.id
        self._load_workspace_context(duplicate.id)
        self._record_operation(
            actor_id="user-exdir",
            action="exercise.duplicated",
            target_type="exercise",
            target_id=duplicate.id,
            result="duplicated",
            activity_title=f"{duplicate.name} Created",
        )
        return self.snapshot()

    def delete_exercise(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        exercise = self._required_active_exercise()
        if len(self.registry.exercises) == 1:
            raise ValueError("cannot delete the only exercise in the store")
        self.registry.exercises = [
            item for item in self.registry.exercises if item.id != exercise.id
        ]
        self.exercise_organization_map.pop(exercise.id, None)
        self.exercise_workspaces.pop(exercise.id, None)
        self.active_exercise_id = self._first_exercise_for_organization(
            self.active_organization_id
        )
        self._load_workspace_context(self.active_exercise_id)
        self._record_operation(
            actor_id="user-exdir",
            action="exercise.deleted",
            target_type="exercise",
            target_id=exercise.id,
            result="deleted",
            activity_title=f"{exercise.name} Deleted",
        )
        return self.snapshot()

    def create_inject(self, payload: dict[str, Any]) -> dict[str, Any]:
        title = str(payload.get("title") or "New Inject").strip()
        controller_id = str(payload.get("assigned_controller") or "user-controller")
        inject = Inject(
            id=_unique_id("inject", [item.id for item in self.registry.injects]),
            exercise_id=self.exercise_id,
            title=title,
            description=str(payload.get("description") or "Created in Forge Studio."),
            inject_type=_enum_value(InjectType, str(payload.get("inject_type") or "other")),
            priority=_enum_value(InjectPriority, str(payload.get("priority") or "medium")),
            status=InjectStatus.PENDING_REVIEW,
            assigned_controller=controller_id,
            created_by=controller_id,
        )
        self.registry.register_inject(inject)
        objective_id = str(payload.get("objective_id") or "").strip()
        if objective_id:
            self.inject_objective_links[inject.id] = objective_id
        review = StudioReviewItem(
            id=_unique_id("review", [item.id for item in self.registry.review_items]),
            exercise_id=self.exercise_id,
            item_type=ReviewItemType.INJECT,
            item_id=inject.id,
            reviewer_id="user-reviewer",
        )
        self.registry.register_review_item(review)
        self._upsert_product_for_inject(inject, "Pending")
        self._register_timeline(
            action="timeline.event.created",
            title=f"{inject.title} Created",
            description=inject.description,
            related_inject_id=inject.id,
        )
        self._record_operation(
            actor_id=controller_id,
            action="inject.created",
            target_type="inject",
            target_id=inject.id,
            result="created",
            activity_title=f"{inject.title} Created",
        )
        return self.snapshot()

    def edit_inject(self, payload: dict[str, Any]) -> dict[str, Any]:
        inject = self._required_inject(_required(payload, "inject_id"))
        if payload.get("title"):
            inject.title = str(payload["title"]).strip()
        if payload.get("description"):
            inject.description = str(payload["description"]).strip()
        if payload.get("inject_type"):
            inject.inject_type = _enum_value(InjectType, str(payload["inject_type"]))
        if payload.get("priority"):
            inject.priority = _enum_value(InjectPriority, str(payload["priority"]))
        if payload.get("assigned_controller"):
            controller_id = str(payload["assigned_controller"]).strip()
            self.registry._required_user(controller_id)
            inject.assigned_controller = controller_id
        if payload.get("objective_id"):
            self.inject_objective_links[inject.id] = str(payload["objective_id"]).strip()
        if payload.get("scheduled_time"):
            scheduled_time = _parse_datetime(payload.get("scheduled_time"))
            if scheduled_time:
                if not inject.releasable:
                    inject.approve("user-reviewer")
                    self._complete_review_for_item(inject.id, ReviewDecision.APPROVED)
                inject.schedule(scheduled_time)
        inject.updated_at = _operation_timestamp()
        self._upsert_product_for_inject(inject, _status_label(inject.status.value))
        self._record_operation(
            actor_id=inject.assigned_controller or "user-controller",
            action="inject.updated",
            target_type="inject",
            target_id=inject.id,
            result="updated",
            activity_title=f"{inject.title} Updated",
        )
        return self.snapshot()

    def delete_inject(self, payload: dict[str, Any]) -> dict[str, Any]:
        inject_id = _required(payload, "inject_id")
        inject = self._required_inject(inject_id)
        self.registry.injects = [item for item in self.registry.injects if item.id != inject_id]
        self.registry.review_items = [
            item for item in self.registry.review_items if item.item_id != inject_id
        ]
        self.inject_objective_links.pop(inject_id, None)
        self.products = [item for item in self.products if item.id != f"product-{inject_id}"]
        self._record_operation(
            actor_id=inject.assigned_controller or "user-controller",
            action="inject.deleted",
            target_type="inject",
            target_id=inject.id,
            result="deleted",
            activity_title=f"{inject.title} Deleted",
        )
        return self.snapshot()

    def create_objective(self, payload: dict[str, Any]) -> dict[str, Any]:
        title = str(payload.get("title") or "New Objective").strip()
        objective = PlanningObjective(
            id=_unique_id("objective", [item.id for item in self.planning_objectives]),
            title=title,
            priority=str(payload.get("priority") or "Medium").strip(),
            success_criteria=_split_list(payload.get("success_criteria")),
            linked_assets=_split_list(payload.get("linked_assets")),
            status=str(payload.get("status") or "Draft").strip(),
        )
        self.planning_objectives.append(objective)
        self.objectives = [item.title for item in self.planning_objectives]
        self._record_operation(
            actor_id="user-exdir",
            action="objective.created",
            target_type="objective",
            target_id=objective.id,
            result="created",
            activity_title=f"{objective.title} Created",
        )
        return self.snapshot()

    def edit_objective(self, payload: dict[str, Any]) -> dict[str, Any]:
        objective = self._required_objective(_required(payload, "objective_id"))
        replacement = PlanningObjective(
            id=objective.id,
            title=str(payload.get("title") or objective.title).strip(),
            priority=str(payload.get("priority") or objective.priority).strip(),
            success_criteria=(
                _split_list(payload.get("success_criteria"))
                if payload.get("success_criteria") is not None
                else list(objective.success_criteria)
            ),
            linked_assets=(
                _split_list(payload.get("linked_assets"))
                if payload.get("linked_assets") is not None
                else list(objective.linked_assets)
            ),
            status=str(payload.get("status") or objective.status).strip(),
        )
        self.planning_objectives = [
            replacement if item.id == objective.id else item
            for item in self.planning_objectives
        ]
        self.objectives = [item.title for item in self.planning_objectives]
        self._record_operation(
            actor_id="user-exdir",
            action="objective.updated",
            target_type="objective",
            target_id=objective.id,
            result="updated",
            activity_title=f"{replacement.title} Updated",
        )
        return self.snapshot()

    def delete_objective(self, payload: dict[str, Any]) -> dict[str, Any]:
        objective = self._required_objective(_required(payload, "objective_id"))
        self.planning_objectives = [
            item for item in self.planning_objectives if item.id != objective.id
        ]
        self.objectives = [item.title for item in self.planning_objectives]
        self.inject_objective_links = {
            inject_id: objective_id
            for inject_id, objective_id in self.inject_objective_links.items()
            if objective_id != objective.id
        }
        self._record_operation(
            actor_id="user-exdir",
            action="objective.deleted",
            target_type="objective",
            target_id=objective.id,
            result="deleted",
            activity_title=f"{objective.title} Deleted",
        )
        return self.snapshot()

    def create_controller(self, payload: dict[str, Any]) -> dict[str, Any]:
        controller = ControllerAssignment(
            id=_unique_id("controller", [item.id for item in self.controllers]),
            role=str(payload.get("role") or "Controller").strip(),
            name=str(payload.get("name") or "New Controller").strip(),
            task=str(payload.get("task") or "Planning support").strip(),
            status=str(payload.get("status") or "Planning").strip(),
            products_today=0,
            pending_reviews=0,
            user_id=str(payload.get("user_id") or "").strip(),
            responsibilities=_split_list(payload.get("responsibilities")),
            linked_objectives=_split_list(payload.get("linked_objectives")),
            linked_injects=_split_list(payload.get("linked_injects")),
        )
        self.controllers.append(controller)
        self._record_operation(
            actor_id="user-exdir",
            action="controller.created",
            target_type="controller",
            target_id=controller.id,
            result="created",
            activity_title=f"{controller.role} Created",
        )
        return self.snapshot()

    def edit_controller(self, payload: dict[str, Any]) -> dict[str, Any]:
        controller = self._required_controller(_required(payload, "controller_id"))
        replacement = ControllerAssignment(
            id=controller.id,
            role=str(payload.get("role") or controller.role).strip(),
            name=str(payload.get("name") or controller.name).strip(),
            task=str(payload.get("task") or controller.task).strip(),
            status=str(payload.get("status") or controller.status).strip(),
            products_today=controller.products_today,
            pending_reviews=controller.pending_reviews,
            user_id=str(payload.get("user_id") or controller.user_id).strip(),
            responsibilities=(
                _split_list(payload.get("responsibilities"))
                if payload.get("responsibilities") is not None
                else list(controller.responsibilities)
            ),
            linked_objectives=(
                _split_list(payload.get("linked_objectives"))
                if payload.get("linked_objectives") is not None
                else list(controller.linked_objectives)
            ),
            linked_injects=(
                _split_list(payload.get("linked_injects"))
                if payload.get("linked_injects") is not None
                else list(controller.linked_injects)
            ),
        )
        self.controllers = [
            replacement if item.id == controller.id else item for item in self.controllers
        ]
        self._record_operation(
            actor_id="user-exdir",
            action="controller.updated",
            target_type="controller",
            target_id=controller.id,
            result="updated",
            activity_title=f"{replacement.role} Updated",
        )
        return self.snapshot()

    def save_atlas_draft(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        exercise = self._required_active_exercise()
        exercise.transition_status(ExerciseStatus.PLANNING)
        self._record_operation(
            actor_id="user-exdir",
            action="atlas.draft.saved",
            target_type="exercise",
            target_id=exercise.id,
            result="saved",
            activity_title=f"{exercise.name} Draft Saved",
        )
        return self.snapshot()

    def validate_atlas_plan(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        exercise = self._required_active_exercise()
        validation = self._atlas_validation()
        readiness = next(
            item for item in validation["summary"] if item["label"] == "Publish readiness"
        )
        self._record_operation(
            actor_id="user-exdir",
            action="atlas.plan.validated",
            target_type="exercise",
            target_id=exercise.id,
            result=readiness["status"].lower().replace(" ", "_"),
            activity_title=f"{exercise.name} Validated",
        )
        return self.snapshot()

    def publish_atlas_plan(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        exercise = self._required_active_exercise()
        self._record_operation(
            actor_id="user-exdir",
            action="atlas.publish.requested",
            target_type="exercise",
            target_id=exercise.id,
            result="human_approval_required",
            activity_title=f"{exercise.name} Publish Requested",
        )
        return self.snapshot()

    def export_atlas_plan(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        exercise = self._required_active_exercise()
        self._record_operation(
            actor_id="user-exdir",
            action="atlas.plan.exported",
            target_type="exercise",
            target_id=exercise.id,
            result="dry_run",
            activity_title=f"{exercise.name} Plan Exported",
        )
        return self.snapshot()

    def approve_inject(self, payload: dict[str, Any]) -> dict[str, Any]:
        inject = self._required_inject(_required(payload, "inject_id"))
        inject.approve("user-reviewer")
        self._complete_review_for_item(inject.id, ReviewDecision.APPROVED)
        self._upsert_product_for_inject(inject, "Approved")
        self._record_operation(
            actor_id="user-reviewer",
            action="inject.approved",
            target_type="inject",
            target_id=inject.id,
            result="approved",
            activity_title=f"{inject.title} Approved",
        )
        return self.snapshot()

    def reject_inject(self, payload: dict[str, Any]) -> dict[str, Any]:
        inject = self._required_inject(_required(payload, "inject_id"))
        inject.reject()
        self._complete_review_for_item(inject.id, ReviewDecision.REJECTED)
        self._upsert_product_for_inject(inject, "Rejected")
        self._record_operation(
            actor_id="user-reviewer",
            action="inject.rejected",
            target_type="inject",
            target_id=inject.id,
            result="rejected",
            activity_title=f"{inject.title} Rejected",
        )
        return self.snapshot()

    def assign_inject_controller(self, payload: dict[str, Any]) -> dict[str, Any]:
        inject = self._required_inject(_required(payload, "inject_id"))
        controller_id = str(payload.get("assigned_controller") or "user-controller")
        self.registry._required_user(controller_id)
        inject.assigned_controller = controller_id
        inject.updated_at = _operation_timestamp()
        self._record_operation(
            actor_id="user-exdir",
            action="inject.assigned",
            target_type="inject",
            target_id=inject.id,
            result="assigned",
            activity_title=f"{inject.title} Assigned",
        )
        return self.snapshot()

    def schedule_inject(self, payload: dict[str, Any]) -> dict[str, Any]:
        inject = self._required_inject(_required(payload, "inject_id"))
        if not inject.releasable:
            inject.approve("user-reviewer")
            self._complete_review_for_item(inject.id, ReviewDecision.APPROVED)
        inject.schedule(_parse_datetime(payload.get("scheduled_time")) or _operation_timestamp())
        self._upsert_product_for_inject(inject, "Scheduled")
        self._record_operation(
            actor_id="user-reviewer",
            action="inject.scheduled",
            target_type="inject",
            target_id=inject.id,
            result="scheduled",
            activity_title=f"{inject.title} Scheduled",
        )
        return self.snapshot()

    def record_timeline_event(
        self,
        *,
        title: str,
        description: str,
        source: str = "exercise_control",
        actor_id: str = "user-exdir",
        timestamp: datetime | None = None,
        event_type: TimelineEventType = TimelineEventType.NOTE,
    ) -> dict[str, Any]:
        event = TimelineEvent(
            id=f"timeline-{len(self.registry.timeline_events) + 1:03d}",
            exercise_id=self.exercise_id,
            event_type=event_type,
            title=title,
            description=description,
            timestamp=timestamp or _operation_timestamp(),
            source=source,
        )
        self.registry.register_timeline_event(event)
        self._record_operation(
            actor_id=actor_id,
            action="timeline.event.created",
            target_type="timeline_event",
            target_id=event.id,
            result="created",
            activity_title=title,
        )
        return self.snapshot()

    def create_timeline_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.record_timeline_event(
            title=str(payload.get("title") or "Timeline Event"),
            description=str(payload.get("description") or "Created in Forge Studio."),
            source=str(payload.get("source") or "exercise_control"),
            timestamp=_parse_datetime(payload.get("timestamp")),
            event_type=_enum_value(TimelineEventType, str(payload.get("event_type") or "note")),
        )

    def edit_timeline_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        event_id = _required(payload, "event_id")
        event = self._required_timeline_event(event_id)
        replacement = TimelineEvent(
            id=event.id,
            exercise_id=event.exercise_id,
            event_type=event.event_type,
            title=str(payload.get("title") or event.title),
            description=str(payload.get("description") or event.description),
            timestamp=_parse_datetime(payload.get("timestamp")) or event.timestamp,
            source=str(payload.get("source") or event.source),
            related_inject_id=event.related_inject_id,
        )
        self._replace_timeline_event(replacement)
        self._record_operation(
            actor_id="user-exdir",
            action="timeline.event.updated",
            target_type="timeline_event",
            target_id=event.id,
            result="updated",
            activity_title=f"{replacement.title} Updated",
        )
        return self.snapshot()

    def delete_timeline_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        event_id = _required(payload, "event_id")
        event = self._required_timeline_event(event_id)
        self.registry.timeline_events = [
            item for item in self.registry.timeline_events if item.id != event_id
        ]
        self._record_operation(
            actor_id="user-exdir",
            action="timeline.event.deleted",
            target_type="timeline_event",
            target_id=event.id,
            result="deleted",
            activity_title=f"{event.title} Deleted",
        )
        return self.snapshot()

    def open_product(self, payload: dict[str, Any]) -> dict[str, Any]:
        product = self._required_product(_required(payload, "product_id"))
        self._record_operation(
            actor_id="user-reviewer",
            action="product.opened",
            target_type="product",
            target_id=product.id,
            result="opened",
            activity_title=f"{product.title} Opened",
        )
        return self.snapshot()

    def view_product_metadata(self, payload: dict[str, Any]) -> dict[str, Any]:
        product = self._required_product(_required(payload, "product_id"))
        self._record_operation(
            actor_id="user-reviewer",
            action="product.metadata.viewed",
            target_type="product",
            target_id=product.id,
            result="viewed",
            activity_title=f"{product.title} Metadata Viewed",
        )
        return self.snapshot()

    def view_product_version_history(self, payload: dict[str, Any]) -> dict[str, Any]:
        product = self._required_product(_required(payload, "product_id"))
        self._record_operation(
            actor_id="user-reviewer",
            action="product.version_history.viewed",
            target_type="product",
            target_id=product.id,
            result="viewed",
            activity_title=f"{product.title} Version History Viewed",
        )
        return self.snapshot()

    def archive_product(self, payload: dict[str, Any]) -> dict[str, Any]:
        product = self._required_product(_required(payload, "product_id"))
        self._replace_product(product, status="Archived")
        self._record_operation(
            actor_id="user-reviewer",
            action="product.archived",
            target_type="product",
            target_id=product.id,
            result="archived",
            activity_title=f"{product.title} Archived",
        )
        return self.snapshot()

    def delete_product(self, payload: dict[str, Any]) -> dict[str, Any]:
        product = self._required_product(_required(payload, "product_id"))
        self.products = [item for item in self.products if item.id != product.id]
        self._record_operation(
            actor_id="user-reviewer",
            action="product.deleted",
            target_type="product",
            target_id=product.id,
            result="deleted",
            activity_title=f"{product.title} Deleted",
        )
        return self.snapshot()

    def _record_operation(
        self,
        *,
        actor_id: str,
        action: str,
        target_type: str,
        target_id: str,
        result: str,
        activity_title: str,
    ) -> None:
        timestamp = _operation_timestamp()
        audit_log = AuditLog(
            id=f"audit-{len(self.registry.audit_logs) + 1:03d}",
            exercise_id=self.exercise_id,
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            timestamp=timestamp,
            metadata={"result": result, "source": "forge_studio_mock"},
        )
        self.registry.register_audit_log(audit_log)
        self.activity.insert(0, {"time": _time_label(timestamp), "title": activity_title})
        self.activity[:] = self.activity[:8]

    def _register_timeline(
        self,
        *,
        action: str,
        title: str,
        description: str,
        related_inject_id: str = "",
    ) -> TimelineEvent:
        event = TimelineEvent(
            id=_unique_id("timeline", [item.id for item in self.registry.timeline_events]),
            exercise_id=self.exercise_id,
            event_type=TimelineEventType.INJECT if related_inject_id else TimelineEventType.NOTE,
            title=title,
            description=description,
            timestamp=_operation_timestamp(),
            source="forge_studio",
            related_inject_id=related_inject_id,
        )
        self.registry.register_timeline_event(event)
        return event

    def _review_payload(self, item: Any) -> dict[str, Any]:
        payload = _to_jsonable(item)
        payload["title"] = self._item_title(item.item_id)
        payload["reviewed_by"] = self._user_name(item.reviewer_id) if item.reviewer_id else ""
        payload["timestamp"] = _to_jsonable(item.reviewed_at or item.created_at)
        return payload

    def _inject_payload(self, item: Any) -> dict[str, Any]:
        payload = _to_jsonable(item)
        payload["assigned_controller_name"] = self._user_name(item.assigned_controller)
        payload["approved_by_name"] = self._user_name(item.approved_by) if item.approved_by else ""
        return payload

    def _controller_payload(self, item: ControllerAssignment) -> dict[str, Any]:
        payload = _to_jsonable(item)
        if item.user_id:
            pending_statuses = {StudioReviewStatus.PENDING, StudioReviewStatus.IN_REVIEW}
            injects_by_id = {inject.id: inject for inject in self.registry.injects}
            payload["pending_reviews"] = sum(
                review.status in pending_statuses
                for review in self.registry.review_items
                if injects_by_id.get(review.item_id)
                and injects_by_id[review.item_id].assigned_controller == item.user_id
            )
            payload["products_today"] = sum(
                product.author == item.name for product in self.products
            )
        return payload

    def _audit_payload(self, item: AuditLog) -> dict[str, Any]:
        payload = _to_jsonable(item)
        payload["actor"] = self._user_name(item.actor_id)
        payload["target"] = f"{item.target_type}:{item.target_id}"
        payload["result"] = str(
            item.metadata.get("result") or item.metadata.get("status") or "recorded"
        )
        return payload

    def _item_title(self, item_id: str) -> str:
        inject = self.registry.get_inject(item_id)
        if inject:
            return inject.title
        for product in self.products:
            if product.id == item_id:
                return product.title
        return item_id

    def _user_name(self, user_id: str) -> str:
        user = self.registry.get_user(user_id)
        return user.display_name if user else user_id

    def _active_exercise(self) -> Exercise | None:
        if self.active_exercise_id:
            exercise = self.registry.get_exercise(self.active_exercise_id)
            if exercise:
                return exercise
        exercises = self.registry.list_exercises()
        return exercises[0] if exercises else None

    def _required_active_exercise(self) -> Exercise:
        exercise = self._active_exercise()
        if exercise is None:
            raise ValueError("exercise store requires one active exercise")
        return exercise

    def _required_inject(self, inject_id: str) -> Inject:
        inject = self.registry.get_inject(inject_id)
        if inject is None:
            raise ValueError(f"inject not found: {inject_id}")
        return inject

    def _required_review(self, review_id: str) -> StudioReviewItem:
        review = self.registry.get_review_item(review_id)
        if review is None:
            raise ValueError(f"review not found: {review_id}")
        return review

    def _required_timeline_event(self, event_id: str) -> TimelineEvent:
        event = self.registry.get_timeline_event(event_id)
        if event is None:
            raise ValueError(f"timeline event not found: {event_id}")
        return event

    def _required_product(self, product_id: str) -> ExerciseProduct:
        for product in self.products:
            if product.id == product_id:
                return product
        raise ValueError(f"product not found: {product_id}")

    def _required_objective(self, objective_id: str) -> PlanningObjective:
        for objective in self.planning_objectives:
            if objective.id == objective_id:
                return objective
        raise ValueError(f"objective not found: {objective_id}")

    def _required_controller(self, controller_id: str) -> ControllerAssignment:
        for controller in self.controllers:
            if controller.id == controller_id:
                return controller
        raise ValueError(f"controller not found: {controller_id}")

    def _replace_timeline_event(self, replacement: TimelineEvent) -> None:
        self.registry.timeline_events = [
            replacement if item.id == replacement.id else item
            for item in self.registry.timeline_events
        ]
        self.registry.timeline_events.sort(key=lambda item: item.timestamp)

    def _replace_product(
        self,
        product: ExerciseProduct,
        *,
        status: str | None = None,
        review_status: str | None = None,
        title: str | None = None,
    ) -> None:
        replacement = ExerciseProduct(
            id=product.id,
            folder=product.folder,
            product_type=product.product_type,
            title=title or product.title,
            status=status or product.status,
            version=product.version,
            last_updated=self.operational_time,
            author=product.author,
            review_status=review_status or product.review_status,
            metadata=dict(product.metadata),
            version_history=[*product.version_history, product.version],
        )
        self.products = [replacement if item.id == product.id else item for item in self.products]

    def _upsert_product_for_inject(self, inject: Inject, review_status: str) -> None:
        product_id = f"product-{inject.id}"
        existing = next((item for item in self.products if item.id == product_id), None)
        if existing:
            self._replace_product(
                existing,
                status=_status_label(inject.status.value),
                review_status=review_status,
                title=f"{inject.title} Packet",
            )
            return
        self.products.insert(
            0,
            ExerciseProduct(
                id=product_id,
                folder="Injects",
                product_type="Inject",
                title=f"{inject.title} Packet",
                status=_status_label(inject.status.value),
                version="v0.1",
                last_updated=self.operational_time,
                author=self._user_name(inject.assigned_controller),
                review_status=review_status,
                metadata={"source": "inject", "inject_id": inject.id},
                version_history=["v0.1"],
            ),
        )

    def _sync_product_review_status(self, item_id: str, review_status: str) -> None:
        product = next((item for item in self.products if item.id == item_id), None)
        if product:
            self._replace_product(product, review_status=review_status)

    def _complete_review_for_item(self, item_id: str, decision: ReviewDecision) -> None:
        for item in self.registry.review_items:
            if item.item_id == item_id and item.status in {
                StudioReviewStatus.PENDING,
                StudioReviewStatus.IN_REVIEW,
            }:
                item.record_decision(decision, "user-reviewer")
                break

    def _required_active_organization(self) -> Organization:
        for organization in self.organizations:
            if organization.id == self.active_organization_id:
                return organization
        raise ValueError(f"organization not found: {self.active_organization_id}")

    def _exercises_for_active_organization(self) -> list[Exercise]:
        return [
            exercise
            for exercise in self.registry.list_exercises()
            if self.exercise_organization_map.get(exercise.id) == self.active_organization_id
        ]

    def _first_exercise_for_organization(self, organization_id: str) -> str:
        exercises = [
            exercise
            for exercise in self.registry.list_exercises()
            if self.exercise_organization_map.get(exercise.id) == organization_id
        ]
        preferred_statuses = (
            ExerciseStatus.ACTIVE,
            ExerciseStatus.PLANNING,
            ExerciseStatus.PREPARING,
            ExerciseStatus.ARCHIVED,
        )
        for status in preferred_statuses:
            for exercise in exercises:
                if exercise.status is status:
                    return exercise.id
        raise ValueError(f"organization has no exercises: {organization_id}")

    def _store_active_workspace_context(self) -> None:
        if not self.active_exercise_id:
            return
        self.exercise_workspaces[self.active_exercise_id] = ExerciseWorkspaceContext(
            products=list(self.products),
            controllers=list(self.controllers),
            library_folders=list(self.library_folders),
            settings=list(self.settings),
            objectives=list(self.objectives),
            participating_units=list(self.participating_units),
            activity=list(self.activity),
            exercise_control=self.exercise_control,
            exercise_director_id=self.exercise_director_id,
            training_audience=self.training_audience,
            timeline_status=self.timeline_status,
            exercise_health=self.exercise_health,
            operational_time=self.operational_time,
            planning_objectives=list(self.planning_objectives),
            inject_objective_links=dict(self.inject_objective_links),
        )

    def _load_workspace_context(self, exercise_id: str) -> None:
        if exercise_id not in self.exercise_workspaces:
            exercise = self.registry.get_exercise(exercise_id)
            self.exercise_workspaces[exercise_id] = _workspace_context_for_exercise(
                exercise or self._required_active_exercise()
            )
        context = self.exercise_workspaces[exercise_id]
        self.products = list(context.products)
        self.controllers = list(context.controllers)
        self.library_folders = list(context.library_folders)
        self.settings = list(context.settings)
        self.objectives = list(context.objectives)
        self.participating_units = list(context.participating_units)
        self.activity = list(context.activity)
        self.exercise_control = context.exercise_control
        self.exercise_director_id = context.exercise_director_id
        self.training_audience = context.training_audience
        self.timeline_status = context.timeline_status
        self.exercise_health = context.exercise_health
        self.operational_time = context.operational_time
        self.planning_objectives = list(context.planning_objectives)
        self.inject_objective_links = dict(context.inject_objective_links)
        if not self.planning_objectives:
            self.planning_objectives = _objectives_from_titles(self.objectives)
        self.objectives = [item.title for item in self.planning_objectives]

    def _mock_search_results(self) -> list[dict[str, str]]:
        exercise = self._required_active_exercise()
        results = [
            {
                "type": "Exercise",
                "title": exercise.name,
                "context": self._required_active_organization().short_name,
            }
        ]
        for inject in self.registry.list_injects(exercise.id)[:2]:
            results.append(
                {"type": "Inject", "title": inject.title, "context": inject.status.value}
            )
        for product in self.products[:2]:
            results.append(
                {"type": "Product", "title": product.title, "context": product.review_status}
            )
        for controller in self.controllers[:2]:
            results.append(
                {"type": "Controller", "title": controller.name, "context": controller.role}
            )
        for event in self.registry.list_timeline_events(exercise.id)[:2]:
            results.append(
                {"type": "Timeline", "title": event.title, "context": _time_label(event.timestamp)}
            )
        return results

    def _designer_payload(
        self,
        exercise: Exercise,
        exercise_workspace: dict[str, Any],
    ) -> dict[str, Any]:
        timeline_events = self.registry.list_timeline_events(exercise.id)
        injects = self.registry.list_injects(exercise.id)
        objective_titles = {item.id: item.title for item in self.planning_objectives}
        inject_titles = {item.id: item.title for item in injects}
        controller_by_user = {
            controller.user_id: controller for controller in self.controllers if controller.user_id
        }
        planning_objects: list[dict[str, Any]] = []
        for event in timeline_events:
            linked_objective_id = self.inject_objective_links.get(event.related_inject_id, "")
            linked_inject_title = inject_titles.get(event.related_inject_id, "")
            planning_objects.append(
                {
                    "id": event.id,
                    "title": event.title,
                    "type": "Timeline Event",
                    "time": _time_label(event.timestamp),
                    "linked_objectives": (
                        [objective_titles[linked_objective_id]]
                        if linked_objective_id in objective_titles
                        else []
                    ),
                    "related_injects": [linked_inject_title] if linked_inject_title else [],
                    "assigned_controller": "Exercise Control",
                    "produced_products": [
                        product.title
                        for product in self.products
                        if product.metadata.get("inject_id") == event.related_inject_id
                    ],
                    "follow_on_events": _next_event_titles(event.id, timeline_events),
                    "validation_warnings": [] if event.timestamp else ["Scheduled time required."],
                    "status": _status_label(event.event_type.value),
                    "notes": event.description,
                }
            )
        for inject in injects:
            controller = controller_by_user.get(inject.assigned_controller)
            objective_id = self.inject_objective_links.get(inject.id, "")
            warnings = []
            if not objective_id:
                warnings.append("Link this inject to an objective.")
            if not inject.assigned_controller:
                warnings.append("Assign a controller.")
            if not inject.scheduled_time:
                warnings.append("Assign planned time before publish.")
            planning_objects.append(
                {
                    "id": inject.id,
                    "title": inject.title,
                    "type": "Inject",
                    "time": _time_label(inject.scheduled_time),
                    "linked_objectives": (
                        [objective_titles[objective_id]] if objective_id in objective_titles else []
                    ),
                    "related_injects": [],
                    "assigned_controller": controller.role if controller else self._user_name(
                        inject.assigned_controller
                    ),
                    "produced_products": [
                        product.title
                        for product in self.products
                        if product.metadata.get("inject_id") == inject.id
                    ],
                    "follow_on_events": [
                        event.title
                        for event in timeline_events
                        if event.related_inject_id == inject.id
                    ],
                    "validation_warnings": warnings,
                    "status": _status_label(inject.status.value),
                    "notes": inject.description,
                }
            )
        planning_objects.sort(key=lambda item: item["time"] if item["time"] != "--" else "9999")
        validation = self._atlas_validation()
        exercise_assets = (
            [
                {"id": item.id, "title": item.title, "type": "Objective"}
                for item in self.planning_objectives
            ]
            + [
                {"id": item.id, "title": item.title, "type": "Inject"}
                for item in injects
            ]
            + [
                {"id": item.id, "title": item.title, "type": "Timeline Event"}
                for item in timeline_events
            ]
            + [
                {"id": item.id, "title": item.role, "type": "Controller"}
                for item in self.controllers
            ]
            + [
                {"id": item.id, "title": item.title, "type": "Product"}
                for item in self.products
            ]
            + [
                {
                    "id": "observation-route-control",
                    "title": "Route Control Observation",
                    "type": "Observation",
                },
                {
                    "id": "aar-finding-route-control",
                    "title": "Route Control AAR Finding",
                    "type": "AAR Finding",
                },
            ]
        )
        relationships = []
        for inject_id, objective_id in self.inject_objective_links.items():
            relationships.append(
                {"source": objective_id, "target": inject_id, "type": "supports"}
            )
        for inject in injects:
            controller = controller_by_user.get(inject.assigned_controller)
            if controller:
                relationships.append(
                    {"source": inject.id, "target": controller.id, "type": "assigned_to"}
                )
        return {
            "name": "Project Atlas",
            "purpose": "Interactive Exercise Designer planning environment",
            "reference": "Project Sentinel",
            "asset_types": [
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
            ],
            "relationship_types": [
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
            ],
            "exercise_assets": exercise_assets,
            "relationships": relationships,
            "object_categories": [
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
            ],
            "toolbar": ["New Exercise", "Save Draft", "Validate", "Publish", "Export"],
            "exercise_properties": {
                "Exercise Name": exercise.name,
                "Organization": self._required_active_organization().name,
                "Phase": exercise_workspace["phase"],
                "Status": exercise_workspace["status"],
                "Exercise Director": str(exercise_workspace["exercise_director"]),
                "Start Date": _to_jsonable(exercise.start_date) or "",
                "End Date": _to_jsonable(exercise.end_date) or "",
                "Training Audience": str(exercise_workspace["training_audience"]),
                "Description": exercise.description,
            },
            "objectives": [_to_jsonable(item) for item in self.planning_objectives],
            "controllers": [self._controller_payload(item) for item in self.controllers],
            "injects": [self._inject_payload(item) for item in injects],
            "timeline_events": [_to_jsonable(item) for item in timeline_events],
            "planning_objects": planning_objects,
            "relationship_map": self._atlas_relationship_map(),
            "validation": validation["summary"],
            "relationship_validation": validation["relationships"],
        }

    def _atlas_validation(self) -> dict[str, list[dict[str, str]]]:
        injects = self.registry.list_injects(self.exercise_id)
        timeline_events = self.registry.list_timeline_events(self.exercise_id)
        objective_issues = sum(
            not item.success_criteria or not item.linked_assets
            for item in self.planning_objectives
        )
        controller_issues = sum(not item.assigned_controller for item in injects)
        missing_relationships = sum(
            inject.id not in self.inject_objective_links for inject in injects
        )
        time_counts: dict[str, int] = {}
        for event in timeline_events:
            key = _time_label(event.timestamp)
            time_counts[key] = time_counts.get(key, 0) + 1
        timeline_conflicts = sum(count > 1 for count in time_counts.values())
        pending_reviews = self.statistics()["pending_reviews"]
        ready = not (
            objective_issues
            or controller_issues
            or missing_relationships
            or timeline_conflicts
            or pending_reviews
        )
        return {
            "summary": [
                _validation_item("Objectives complete", objective_issues),
                _validation_item("Controllers assigned", controller_issues),
                _validation_item("Timeline conflicts", timeline_conflicts),
                _validation_item("Missing relationships", missing_relationships),
                {
                    "label": "Publish readiness",
                    "status": "Ready" if ready else "Not ready",
                    "state": "success" if ready else "danger",
                },
            ],
            "relationships": [
                _validation_item(
                    "Inject objective links",
                    missing_relationships,
                    "Injects should link to at least one objective.",
                ),
                _validation_item(
                    "Controller assignments",
                    controller_issues,
                    "Injects should have an assigned controller.",
                ),
                _validation_item(
                    "Scheduled timeline events",
                    sum(not event.timestamp for event in timeline_events),
                    "Timeline events should have a scheduled time.",
                ),
                _validation_item(
                    "Product source references",
                    sum(
                        not (
                            product.metadata.get("inject_id")
                            or product.metadata.get("source_event_id")
                            or product.metadata.get("exercise")
                        )
                        for product in self.products
                    ),
                    "Products should reference a source event or inject.",
                ),
                {
                    "label": "AAR traceability",
                    "status": "Complete",
                    "state": "success",
                    "rule": "AAR findings should trace back to an objective or observation.",
                },
            ],
        }

    def _atlas_relationship_map(self) -> dict[str, Any]:
        objective_titles = {item.id: item.title for item in self.planning_objectives}
        injects_by_id = {item.id: item for item in self.registry.list_injects(self.exercise_id)}
        chain = [self._required_active_exercise().name]
        first_objective = self.planning_objectives[0] if self.planning_objectives else None
        if first_objective:
            chain.append(first_objective.title)
            linked_inject = next(
                (
                    injects_by_id[inject_id]
                    for inject_id, objective_id in self.inject_objective_links.items()
                    if objective_id == first_objective.id and inject_id in injects_by_id
                ),
                None,
            )
            if linked_inject:
                chain.append(linked_inject.title)
                controller = self._user_name(linked_inject.assigned_controller)
                if controller:
                    chain.append(controller)
                event = next(
                    (
                        item
                        for item in self.registry.list_timeline_events(self.exercise_id)
                        if item.related_inject_id == linked_inject.id
                    ),
                    None,
                )
                if event:
                    chain.append(event.title)
        if len(chain) < 3 and objective_titles:
            chain.extend(list(objective_titles.values())[:2])
        chain.append("AAR Finding")
        return {"title": "Live Atlas Relationship Chain", "chain": chain}

    def _knowledge_graph_payload(
        self,
        exercise: Exercise,
        organization: Organization,
        exercise_workspace: dict[str, Any],
    ) -> dict[str, Any]:
        created = _to_jsonable(exercise.created_at)
        modified = _to_jsonable(exercise.updated_at)
        nodes: list[dict[str, Any]] = [
            _graph_node(
                "kg-exercise",
                exercise.name,
                "Exercise",
                exercise.description or "Active exercise package and graph root.",
                exercise.name,
                exercise_workspace["status"],
                created,
                modified,
                50,
                50,
            ),
            _graph_node(
                "kg-organization",
                organization.short_name,
                "Organization",
                organization.name,
                exercise.name,
                "Active",
                created,
                modified,
                18,
                15,
            ),
        ]
        edges = [{"source": "kg-organization", "target": "kg-exercise", "type": "contains"}]
        for index, objective in enumerate(self.planning_objectives):
            node_id = f"kg-{objective.id}"
            nodes.append(
                _graph_node(
                    node_id,
                    objective.title,
                    "Objective",
                    "; ".join(objective.success_criteria) or "Planning objective.",
                    exercise.name,
                    objective.status,
                    created,
                    modified,
                    24 + (index % 3) * 18,
                    28 + (index // 3) * 14,
                )
            )
            edges.append({"source": "kg-exercise", "target": node_id, "type": "contains"})
        for index, controller in enumerate(self.controllers[:8]):
            node_id = f"kg-{controller.id}"
            nodes.append(
                _graph_node(
                    node_id,
                    controller.role,
                    "Controller",
                    controller.task,
                    exercise.name,
                    controller.status,
                    created,
                    modified,
                    16 + (index % 4) * 20,
                    70 + (index // 4) * 12,
                )
            )
            edges.append({"source": "kg-exercise", "target": node_id, "type": "contains"})
            for objective_id in controller.linked_objectives:
                edges.append(
                    {
                        "source": node_id,
                        "target": f"kg-{objective_id}",
                        "type": "assigned_to",
                    }
                )
        controllers_by_user = {
            controller.user_id: controller for controller in self.controllers if controller.user_id
        }
        for index, inject in enumerate(self.registry.list_injects(exercise.id)):
            node_id = f"kg-{inject.id}"
            nodes.append(
                _graph_node(
                    node_id,
                    inject.title,
                    "Inject",
                    inject.description,
                    exercise.name,
                    _status_label(inject.status.value),
                    _to_jsonable(inject.created_at),
                    _to_jsonable(inject.updated_at),
                    52 + (index % 3) * 14,
                    24 + (index // 3) * 12,
                )
            )
            objective_id = self.inject_objective_links.get(inject.id)
            if objective_id:
                edges.append(
                    {"source": f"kg-{objective_id}", "target": node_id, "type": "supports"}
                )
            controller = controllers_by_user.get(inject.assigned_controller)
            if controller:
                edges.append(
                    {
                        "source": node_id,
                        "target": f"kg-{controller.id}",
                        "type": "assigned_to",
                    }
                )
        for index, event in enumerate(self.registry.list_timeline_events(exercise.id)):
            node_id = f"kg-{event.id}"
            nodes.append(
                _graph_node(
                    node_id,
                    event.title,
                    "Timeline Event",
                    event.description,
                    exercise.name,
                    _status_label(event.event_type.value),
                    created,
                    modified,
                    30 + (index % 4) * 16,
                    84,
                )
            )
            edges.append({"source": "kg-exercise", "target": node_id, "type": "contains"})
            if event.related_inject_id:
                edges.append(
                    {
                        "source": f"kg-{event.related_inject_id}",
                        "target": node_id,
                        "type": "triggers",
                    }
                )
        for index, product in enumerate(self.products[:10]):
            node_id = f"kg-{product.id}"
            nodes.append(
                _graph_node(
                    node_id,
                    product.title,
                    "Product",
                    product.product_type,
                    exercise.name,
                    product.status,
                    created,
                    modified,
                    78,
                    18 + index * 7,
                )
            )
            if product.metadata.get("inject_id"):
                edges.append(
                    {
                        "source": f"kg-{product.metadata['inject_id']}",
                        "target": node_id,
                        "type": "produces",
                    }
                )
        nodes = [_node_with_relationship_metadata(node, nodes, edges) for node in nodes]
        return {
            "name": "Forge Operational Knowledge Graph",
            "purpose": "Connected intelligence layer for operational assets.",
            "node_types": [
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
            ],
            "relationship_types": [
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
            ],
            "nodes": nodes,
            "edges": edges,
            "default_node_id": "kg-exercise",
            "filters": [
                "Objectives",
                "Injects",
                "Controllers",
                "Products",
                "Weather",
                "Intelligence",
                "Observations",
                "Timeline Events",
                "AAR Findings",
            ],
            "filter_map": {
                "Objectives": ["Objective"],
                "Injects": ["Inject"],
                "Controllers": ["Controller"],
                "Products": ["Product"],
                "Weather": ["Weather Event"],
                "Intelligence": ["Intelligence Update"],
                "Observations": ["Observation"],
                "Timeline Events": ["Timeline Event", "Decision Point"],
                "AAR Findings": ["AAR Finding"],
            },
            "navigation": [
                "Click node",
                "Expand neighbors",
                "Collapse neighbors",
                "Center graph",
                "Filter by asset type",
                "Search",
                "Relationship highlighting",
            ],
        }


def create_mock_exercise_store(registry: ForgeStudioRegistry | None = None) -> ExerciseStore:
    """Create the shared Exercise Data Engine for Mountain Exercise 3-27."""

    registry = registry or create_mock_registry()
    _seed_platform_exercises(registry)
    organizations = _default_organizations()
    exercise_organization_map = _mock_exercise_organization_map()
    sentinel_objectives = [
        PlanningObjective(
            id="objective-command-control",
            title="Exercise command and control in complex mountain terrain.",
            priority="Critical",
            success_criteria=[
                "Training audience maintains command rhythm during route disruption.",
                "Commander decision points are recorded with rationale.",
            ],
            linked_assets=["inject-002", "timeline-008", "controller-exdir"],
            status="Ready",
        ),
        PlanningObjective(
            id="objective-intel-fusion",
            title="Evaluate intelligence-to-operations handoff under time pressure.",
            priority="High",
            success_criteria=[
                "Intelligence baseline reaches the training audience before movement.",
                "ISR updates drive at least one operational decision.",
            ],
            linked_assets=["inject-005", "timeline-002", "controller-intel"],
            status="Ready",
        ),
        PlanningObjective(
            id="objective-medical-logistics",
            title="Validate casualty evacuation and route disruption procedures.",
            priority="High",
            success_criteria=[
                "Unit coordinates MEDEVAC under weather and route constraints.",
                "Route disruption decisions are visible in the exercise timeline.",
            ],
            linked_assets=["inject-008", "inject-007", "controller-white"],
            status="Draft",
        ),
        PlanningObjective(
            id="objective-info-environment",
            title="Assess media, cyber, and weather inject response.",
            priority="Medium",
            success_criteria=[
                "Media, cyber, and weather controllers synchronize inject timing.",
                "Review queue captures human approval before release.",
            ],
            linked_assets=["inject-003", "inject-004", "inject-006"],
            status="Needs Review",
        ),
    ]
    mountain_context = ExerciseWorkspaceContext(
        products=_mock_products(),
        controllers=_mock_controllers(),
        library_folders=_library_folders(),
        settings=_settings(),
        objectives=[item.title for item in sentinel_objectives],
        participating_units=[
            "2d Battalion, 8th Marines",
            "Mountain Warfare Training Center",
            "Bridgeport EXCON",
            "Blue Force Role Players",
            "Simulated Media Cell",
        ],
        activity=[
            {"time": "0937", "title": "Intelligence Update Published"},
            {"time": "0935", "title": "Cyber Inject Approved"},
            {"time": "0931", "title": "Media Story Released"},
            {"time": "0926", "title": "Weather Updated"},
            {"time": "0920", "title": "Blue Force Report Received"},
        ],
        exercise_control="Bridgeport EXCON",
        exercise_director_id="user-exdir",
        training_audience="2d Battalion, 8th Marines",
        timeline_status="On Plan",
        exercise_health="Nominal",
        operational_time="0942",
        planning_objectives=sentinel_objectives,
        inject_objective_links={
            "inject-002": "objective-command-control",
            "inject-003": "objective-info-environment",
            "inject-004": "objective-info-environment",
            "inject-005": "objective-intel-fusion",
            "inject-006": "objective-info-environment",
            "inject-007": "objective-medical-logistics",
            "inject-008": "objective-medical-logistics",
        },
    )
    exercise_workspaces = {
        "mountain-exercise-3-27": mountain_context,
        "winter-mountain-leaders-course": _workspace_context_for_exercise(
            registry._required_exercise("winter-mountain-leaders-course")
        ),
        "itx-2-27": _workspace_context_for_exercise(registry._required_exercise("itx-2-27")),
        "mountain-exercise-2-27": _workspace_context_for_exercise(
            registry._required_exercise("mountain-exercise-2-27")
        ),
        "advanced-naval-technology-experiment-27": _workspace_context_for_exercise(
            registry._required_exercise("advanced-naval-technology-experiment-27")
        ),
        "tecom-staff-exercise-27": _workspace_context_for_exercise(
            registry._required_exercise("tecom-staff-exercise-27")
        ),
        "joint-training-environment-27": _workspace_context_for_exercise(
            registry._required_exercise("joint-training-environment-27")
        ),
    }
    return ExerciseStore(
        registry=registry,
        organizations=organizations,
        active_organization_id="mwtc",
        active_exercise_id="mountain-exercise-3-27",
        exercise_organization_map=exercise_organization_map,
        exercise_workspaces=exercise_workspaces,
    )


def _default_organizations() -> list[Organization]:
    return [
        Organization(
            id="mwtc",
            name="Marine Corps Mountain Warfare Training Center",
            short_name="MWTC",
        ),
        Organization(
            id="eotg",
            name="Expeditionary Operations Training Group",
            short_name="EOTG",
        ),
        Organization(
            id="mcwl",
            name="Marine Corps Warfighting Laboratory",
            short_name="MCWL",
        ),
        Organization(
            id="tecom",
            name="Training and Education Command",
            short_name="TECOM",
        ),
        Organization(
            id="jte",
            name="Joint Training Environment",
            short_name="JTE",
        ),
    ]


def _workspace_definitions() -> list[dict[str, str]]:
    return [
        {"id": "mission-control", "label": "Mission Control", "icon": "MC"},
        {"id": "exercise-designer", "label": "Exercise Designer", "icon": "ED"},
        {"id": "knowledge-graph", "label": "Knowledge Graph", "icon": "KG"},
        {"id": "timeline", "label": "Timeline", "icon": "TL"},
        {"id": "intelligence", "label": "Intelligence", "icon": "IN"},
        {"id": "inject-library", "label": "Inject Library", "icon": "IJ"},
        {"id": "exercise-library", "label": "Exercise Library", "icon": "LB"},
        {"id": "controllers", "label": "Controllers", "icon": "CT"},
        {"id": "review-queue", "label": "Review Queue", "icon": "RV"},
        {"id": "reports", "label": "Reports", "icon": "RP"},
        {"id": "analytics", "label": "Analytics", "icon": "AN"},
        {"id": "administration", "label": "Administration", "icon": "AD"},
    ]


def _designer_payload(exercise: Exercise, exercise_workspace: dict[str, Any]) -> dict[str, Any]:
    planning_objects = [
        {
            "id": "atlas-001",
            "title": "STARTEX",
            "type": "Timeline Event",
            "time": "0800",
            "linked_objective": "Exercise command and control in complex mountain terrain.",
            "linked_objectives": ["Objective Alpha"],
            "related_injects": [],
            "assigned_controller": "Exercise Director",
            "produced_products": ["STARTEX Control Note"],
            "follow_on_events": ["Intelligence Baseline"],
            "validation_warnings": [],
            "status": "Ready",
            "notes": "Begin execution lane and establish controller battle rhythm.",
        },
        {
            "id": "atlas-002",
            "title": "Intelligence Baseline",
            "type": "Intelligence Update",
            "time": "0810",
            "linked_objective": "Evaluate intelligence-to-operations handoff under time pressure.",
            "linked_objectives": ["Objective Bravo"],
            "related_injects": ["Civilian Protest"],
            "assigned_controller": "Intelligence Controller",
            "produced_products": ["Intelligence Baseline Product"],
            "follow_on_events": ["Civilian Protest"],
            "validation_warnings": [],
            "status": "Draft",
            "notes": "Initial intelligence picture for training audience orientation.",
        },
        {
            "id": "atlas-003",
            "title": "Weather Impact Inject",
            "type": "Weather Event",
            "time": "0905",
            "linked_objective": "Assess media, cyber, and weather inject response.",
            "linked_objectives": ["Objective Charlie"],
            "related_injects": ["Avalanche Warning"],
            "assigned_controller": "Weather Controller",
            "produced_products": ["Weather Impact Advisory"],
            "follow_on_events": ["GPS Interference"],
            "validation_warnings": ["Review required before publish."],
            "status": "Needs Review",
            "notes": "Avalanche risk and visibility constraints affect route movement.",
        },
        {
            "id": "atlas-004",
            "title": "Civilian Protest",
            "type": "Inject",
            "time": "0825",
            "linked_objective": "Validate casualty evacuation and route disruption procedures.",
            "linked_objectives": ["Objective Delta"],
            "related_injects": ["Media Interview"],
            "assigned_controller": "White Cell Controller",
            "produced_products": ["Civilian Protest Inject Card"],
            "follow_on_events": ["Commander Decision Point"],
            "validation_warnings": [],
            "status": "Planned",
            "notes": "Role player lane requires review before execution handoff.",
        },
        {
            "id": "atlas-005",
            "title": "GPS Interference",
            "type": "Decision Point",
            "time": "0935",
            "linked_objective": "Assess media, cyber, and weather inject response.",
            "linked_objectives": ["Objective Charlie"],
            "related_injects": ["GPS Interference Inject"],
            "assigned_controller": "Cyber Controller",
            "produced_products": ["Cyber Effects Summary"],
            "follow_on_events": ["Commander Decision Point"],
            "validation_warnings": ["Timeline conflict with Weather Impact Inject."],
            "status": "Planned",
            "notes": "Cyber cell inject supports commander's navigation decision.",
        },
        {
            "id": "atlas-006",
            "title": "Commander Decision Point",
            "type": "Decision Point",
            "time": "0940",
            "linked_objective": "Exercise command and control in complex mountain terrain.",
            "linked_objectives": ["Objective Alpha"],
            "related_injects": ["Civilian Protest", "GPS Interference"],
            "assigned_controller": "Exercise Director",
            "produced_products": ["Commander Decision Record"],
            "follow_on_events": ["Observer Checkpoint"],
            "validation_warnings": ["Human approval required before execution handoff."],
            "status": "Requires Approval",
            "notes": "Decision point should not publish until EXDIR validates scenario timing.",
        },
        {
            "id": "atlas-007",
            "title": "ENDEX",
            "type": "Timeline Event",
            "time": "1800",
            "linked_objective": "Exercise command and control in complex mountain terrain.",
            "linked_objectives": ["Objective Alpha"],
            "related_injects": [],
            "assigned_controller": "Exercise Director",
            "produced_products": ["ENDEX Assessment Note"],
            "follow_on_events": ["AAR Finding"],
            "validation_warnings": [],
            "status": "Draft",
            "notes": "Close execution lane and prepare assessment archive.",
        },
    ]
    exercise_assets = [
        {"id": "obj-alpha", "title": "Objective Alpha", "type": "Objective"},
        {"id": "inject-civilian-protest", "title": "Civilian Protest", "type": "Inject"},
        {
            "id": "timeline-commander-decision",
            "title": "Commander Decision Point",
            "type": "Timeline Event",
        },
        {"id": "controller-exdir", "title": "Exercise Director", "type": "Controller"},
        {
            "id": "product-intel-baseline",
            "title": "Intelligence Baseline Product",
            "type": "Product",
        },
        {"id": "intel-baseline", "title": "Intelligence Baseline", "type": "Intelligence Update"},
        {"id": "weather-impact", "title": "Weather Impact Inject", "type": "Weather Event"},
        {"id": "media-interview", "title": "Media Interview", "type": "Media Event"},
        {
            "id": "observer-checkpoint",
            "title": "Observer Checkpoint",
            "type": "Observer Checkpoint",
        },
        {"id": "observation-001", "title": "Route Control Observation", "type": "Observation"},
        {"id": "aar-finding-001", "title": "AAR Finding", "type": "AAR Finding"},
    ]
    relationships = [
        {"source": "obj-alpha", "target": "intel-baseline", "type": "supports"},
        {"source": "intel-baseline", "target": "inject-civilian-protest", "type": "triggers"},
        {"source": "inject-civilian-protest", "target": "controller-exdir", "type": "assigned_to"},
        {
            "source": "inject-civilian-protest",
            "target": "product-intel-baseline",
            "type": "produces",
        },
        {
            "source": "weather-impact",
            "target": "timeline-commander-decision",
            "type": "conflicts_with",
        },
        {
            "source": "timeline-commander-decision",
            "target": "observer-checkpoint",
            "type": "follows",
        },
        {"source": "observer-checkpoint", "target": "observation-001", "type": "observes"},
        {"source": "observation-001", "target": "aar-finding-001", "type": "evaluates"},
        {"source": "aar-finding-001", "target": "obj-alpha", "type": "related_to"},
        {"source": "product-intel-baseline", "target": "controller-exdir", "type": "reviews"},
        {
            "source": "timeline-commander-decision",
            "target": "inject-civilian-protest",
            "type": "depends_on",
        },
    ]
    return {
        "name": "Project Atlas",
        "purpose": "Exercise Designer planning environment",
        "asset_types": [
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
        ],
        "relationship_types": [
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
        ],
        "exercise_assets": exercise_assets,
        "relationships": relationships,
        "relationship_map": {
            "title": "Objective Alpha Relationship Chain",
            "chain": [
                "Objective Alpha",
                "Intelligence Baseline",
                "Civilian Protest",
                "Commander Decision Point",
                "Observer Checkpoint",
                "AAR Finding",
            ],
        },
        "object_categories": [
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
        ],
        "planning_objects": planning_objects,
        "exercise_properties": {
            "Exercise Name": exercise.name,
            "Phase": exercise_workspace["phase"],
            "Status": exercise_workspace["status"],
            "Training Audience": str(exercise_workspace["training_audience"]),
            "Exercise Director": str(exercise_workspace["exercise_director"]),
            "Planning Status": "Draft plan ready for validation",
        },
        "validation": [
            {"label": "Objectives linked", "status": "Complete", "state": "success"},
            {"label": "Controllers assigned", "status": "Complete", "state": "success"},
            {"label": "Timeline conflicts", "status": "1 warning", "state": "warning"},
            {"label": "Review requirements", "status": "Required", "state": "warning"},
            {"label": "Publish readiness", "status": "Not ready", "state": "danger"},
        ],
        "relationship_validation": [
            {
                "label": "Inject objective links",
                "status": "1 warning",
                "state": "warning",
                "rule": "Injects should link to at least one objective.",
            },
            {
                "label": "Controller assignments",
                "status": "Complete",
                "state": "success",
                "rule": "Injects should have an assigned controller.",
            },
            {
                "label": "Scheduled timeline events",
                "status": "Complete",
                "state": "success",
                "rule": "Timeline events should have a scheduled time.",
            },
            {
                "label": "Product source references",
                "status": "1 warning",
                "state": "warning",
                "rule": "Products should reference a source event or inject.",
            },
            {
                "label": "AAR traceability",
                "status": "Complete",
                "state": "success",
                "rule": "AAR findings should trace back to an objective or observation.",
            },
        ],
        "toolbar": [
            "New Exercise",
            "Save Draft",
            "Validate",
            "Publish to Mission Control",
            "Export Plan",
        ],
    }


def _knowledge_graph_payload(
    exercise: Exercise,
    organization: Organization,
    exercise_workspace: dict[str, Any],
) -> dict[str, Any]:
    created = "2027-03-01T08:00:00Z"
    modified = "2027-03-01T09:42:00Z"
    exercise_name = exercise.name
    nodes = [
        {
            "id": "kg-exercise",
            "name": exercise.name,
            "type": "Exercise",
            "description": "Active exercise package and graph root.",
            "exercise": exercise_name,
            "status": exercise_workspace["status"],
            "created": created,
            "modified": modified,
            "x": 50,
            "y": 50,
        },
        {
            "id": "kg-organization",
            "name": organization.short_name,
            "type": "Organization",
            "description": organization.name,
            "exercise": exercise_name,
            "status": "Active",
            "created": created,
            "modified": modified,
            "x": 18,
            "y": 15,
        },
        {
            "id": "kg-objective-alpha",
            "name": "Objective Alpha",
            "type": "Objective",
            "description": "Exercise command and control in complex mountain terrain.",
            "exercise": exercise_name,
            "status": "Validated",
            "created": created,
            "modified": modified,
            "x": 28,
            "y": 32,
        },
        {
            "id": "kg-unit-2-8",
            "name": "2/8 Marines",
            "type": "Unit",
            "description": "Primary training audience for Mountain Exercise 3-27.",
            "exercise": exercise_name,
            "status": "Participating",
            "created": created,
            "modified": modified,
            "x": 20,
            "y": 70,
        },
        {
            "id": "kg-controller-exdir",
            "name": "Exercise Director",
            "type": "Controller",
            "description": "Human authority for exercise control and publish decisions.",
            "exercise": exercise_name,
            "status": "Online",
            "created": created,
            "modified": modified,
            "x": 50,
            "y": 20,
        },
        {
            "id": "kg-intel-baseline",
            "name": "Intelligence Baseline",
            "type": "Intelligence Update",
            "description": "Initial intelligence picture for the training audience.",
            "exercise": exercise_name,
            "status": "Draft",
            "created": created,
            "modified": modified,
            "x": 43,
            "y": 35,
        },
        {
            "id": "kg-civilian-protest",
            "name": "Civilian Protest",
            "type": "Inject",
            "description": "Role player disruption inject for route control decisions.",
            "exercise": exercise_name,
            "status": "Planned",
            "created": created,
            "modified": modified,
            "x": 60,
            "y": 44,
        },
        {
            "id": "kg-weather-impact",
            "name": "Weather Impact Inject",
            "type": "Weather Event",
            "description": "Avalanche risk and visibility constraints.",
            "exercise": exercise_name,
            "status": "Needs Review",
            "created": created,
            "modified": modified,
            "x": 72,
            "y": 28,
        },
        {
            "id": "kg-media-interview",
            "name": "Media Interview",
            "type": "Media Event",
            "description": "Simulated press interaction tied to civilian activity.",
            "exercise": exercise_name,
            "status": "Scheduled",
            "created": created,
            "modified": modified,
            "x": 80,
            "y": 58,
        },
        {
            "id": "kg-decision-point",
            "name": "Commander Decision Point",
            "type": "Decision Point",
            "description": "Commander decision during GPS interference and protest injects.",
            "exercise": exercise_name,
            "status": "Requires Approval",
            "created": created,
            "modified": modified,
            "x": 56,
            "y": 72,
        },
        {
            "id": "kg-timeline-0940",
            "name": "0940 Decision Event",
            "type": "Timeline Event",
            "description": "Timeline marker for the commander decision point.",
            "exercise": exercise_name,
            "status": "Planned",
            "created": created,
            "modified": modified,
            "x": 42,
            "y": 82,
        },
        {
            "id": "kg-product-decision",
            "name": "Commander Decision Record",
            "type": "Product",
            "description": "Draft product generated from the decision point.",
            "exercise": exercise_name,
            "status": "Pending Review",
            "created": created,
            "modified": modified,
            "x": 73,
            "y": 82,
        },
        {
            "id": "kg-observation-route",
            "name": "Route Control Observation",
            "type": "Observation",
            "description": "Observer note about route control under conflicting stimuli.",
            "exercise": exercise_name,
            "status": "Captured",
            "created": created,
            "modified": modified,
            "x": 35,
            "y": 58,
        },
        {
            "id": "kg-aar-finding",
            "name": "AAR Finding",
            "type": "AAR Finding",
            "description": "Draft finding connected to objective evidence.",
            "exercise": exercise_name,
            "status": "Draft",
            "created": created,
            "modified": modified,
            "x": 30,
            "y": 88,
        },
        {
            "id": "kg-template-inject",
            "name": "Mountain Inject Template",
            "type": "Template",
            "description": "Reusable planning template inherited by route disruption injects.",
            "exercise": exercise_name,
            "status": "Available",
            "created": created,
            "modified": modified,
            "x": 88,
            "y": 18,
        },
    ]
    edges = [
        {"source": "kg-organization", "target": "kg-exercise", "type": "contains"},
        {"source": "kg-exercise", "target": "kg-objective-alpha", "type": "contains"},
        {"source": "kg-exercise", "target": "kg-unit-2-8", "type": "contains"},
        {"source": "kg-objective-alpha", "target": "kg-intel-baseline", "type": "supports"},
        {"source": "kg-intel-baseline", "target": "kg-civilian-protest", "type": "triggers"},
        {"source": "kg-template-inject", "target": "kg-civilian-protest", "type": "inherits"},
        {"source": "kg-civilian-protest", "target": "kg-controller-exdir", "type": "assigned_to"},
        {"source": "kg-weather-impact", "target": "kg-decision-point", "type": "precedes"},
        {"source": "kg-civilian-protest", "target": "kg-decision-point", "type": "depends_on"},
        {"source": "kg-media-interview", "target": "kg-civilian-protest", "type": "related_to"},
        {"source": "kg-decision-point", "target": "kg-timeline-0940", "type": "references"},
        {"source": "kg-timeline-0940", "target": "kg-decision-point", "type": "follows"},
        {"source": "kg-decision-point", "target": "kg-product-decision", "type": "produces"},
        {"source": "kg-observation-route", "target": "kg-decision-point", "type": "observes"},
        {"source": "kg-aar-finding", "target": "kg-observation-route", "type": "evaluates"},
        {"source": "kg-aar-finding", "target": "kg-objective-alpha", "type": "references"},
    ]
    nodes = [_node_with_relationship_metadata(node, nodes, edges) for node in nodes]
    return {
        "name": "Forge Operational Knowledge Graph",
        "purpose": "Connected intelligence layer for operational assets.",
        "node_types": [
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
        ],
        "relationship_types": [
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
        ],
        "nodes": nodes,
        "edges": edges,
        "default_node_id": "kg-exercise",
        "filters": [
            "Objectives",
            "Injects",
            "Controllers",
            "Products",
            "Weather",
            "Intelligence",
            "Observations",
            "Timeline Events",
            "AAR Findings",
        ],
        "filter_map": {
            "Objectives": ["Objective"],
            "Injects": ["Inject"],
            "Controllers": ["Controller"],
            "Products": ["Product"],
            "Weather": ["Weather Event"],
            "Intelligence": ["Intelligence Update"],
            "Observations": ["Observation"],
            "Timeline Events": ["Timeline Event", "Decision Point"],
            "AAR Findings": ["AAR Finding"],
        },
        "navigation": [
            "Click node",
            "Expand neighbors",
            "Collapse neighbors",
            "Center graph",
            "Filter by asset type",
            "Search",
            "Relationship highlighting",
        ],
    }


def _node_with_relationship_metadata(
    node: dict[str, Any],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, str]],
) -> dict[str, Any]:
    node_names = {item["id"]: item["name"] for item in nodes}
    incoming = [edge for edge in edges if edge["target"] == node["id"]]
    outgoing = [edge for edge in edges if edge["source"] == node["id"]]
    connected_ids = {
        edge["source"] for edge in incoming
    } | {
        edge["target"] for edge in outgoing
    }
    return {
        **node,
        "incoming": incoming,
        "outgoing": outgoing,
        "connected_assets": [
            node_names[item_id] for item_id in sorted(connected_ids) if item_id in node_names
        ],
        "relationship_count": len(incoming) + len(outgoing),
    }


def _mock_exercise_organization_map() -> dict[str, str]:
    return {
        "mountain-exercise-3-27": "mwtc",
        "winter-mountain-leaders-course": "mwtc",
        "mountain-exercise-2-27": "mwtc",
        "itx-2-27": "eotg",
        "advanced-naval-technology-experiment-27": "mcwl",
        "tecom-staff-exercise-27": "tecom",
        "joint-training-environment-27": "jte",
    }


def _seed_platform_exercises(registry: ForgeStudioRegistry) -> None:
    exercises = [
        Exercise(
            id="winter-mountain-leaders-course",
            name="Winter Mountain Leaders Course",
            description="Cold-weather leader training and mountain movement planning lane.",
            status=ExerciseStatus.PLANNING,
            phase=ExercisePhase.PLANNING,
            start_date=datetime(2027, 1, 12, 8, 0, tzinfo=timezone.utc),
            end_date=datetime(2027, 1, 19, 16, 0, tzinfo=timezone.utc),
        ),
        Exercise(
            id="itx-2-27",
            name="ITX 2-27",
            description="Integrated Training Exercise focused on combined arms control.",
            status=ExerciseStatus.ACTIVE,
            phase=ExercisePhase.EXECUTION,
            start_date=datetime(2027, 2, 7, 7, 0, tzinfo=timezone.utc),
            end_date=datetime(2027, 2, 21, 18, 0, tzinfo=timezone.utc),
        ),
        Exercise(
            id="mountain-exercise-2-27",
            name="Mountain Exercise 2-27",
            description="Archived mountain warfare exercise package retained for comparison.",
            status=ExerciseStatus.ARCHIVED,
            phase=ExercisePhase.ASSESSMENT,
            start_date=datetime(2027, 2, 10, 8, 0, tzinfo=timezone.utc),
            end_date=datetime(2027, 2, 17, 18, 0, tzinfo=timezone.utc),
        ),
        Exercise(
            id="advanced-naval-technology-experiment-27",
            name="Advanced Naval Technology Experiment 27",
            description="MCWL experimentation lane for emerging command-and-control workflows.",
            status=ExerciseStatus.PLANNING,
            phase=ExercisePhase.PREPARATION,
            start_date=datetime(2027, 5, 4, 8, 0, tzinfo=timezone.utc),
            end_date=datetime(2027, 5, 8, 17, 0, tzinfo=timezone.utc),
        ),
        Exercise(
            id="tecom-staff-exercise-27",
            name="TECOM Staff Exercise 27",
            description="Training command staff exercise for review, reporting, and assessment.",
            status=ExerciseStatus.PREPARING,
            phase=ExercisePhase.PREPARATION,
            start_date=datetime(2027, 6, 2, 8, 0, tzinfo=timezone.utc),
            end_date=datetime(2027, 6, 6, 16, 0, tzinfo=timezone.utc),
        ),
        Exercise(
            id="joint-training-environment-27",
            name="Joint Training Environment 27",
            description="Joint and coalition exercise control rehearsal environment.",
            status=ExerciseStatus.PLANNING,
            phase=ExercisePhase.PLANNING,
            start_date=datetime(2027, 7, 14, 8, 0, tzinfo=timezone.utc),
            end_date=datetime(2027, 7, 28, 18, 0, tzinfo=timezone.utc),
        ),
    ]
    for exercise in exercises:
        if registry.get_exercise(exercise.id) is None:
            registry.register_exercise(exercise)
            _seed_minimal_exercise_records(registry, exercise)


def _seed_minimal_exercise_records(registry: ForgeStudioRegistry, exercise: Exercise) -> None:
    prefix = exercise.id.split("-")[0]
    controller_id = "user-controller"
    reviewer_id = "user-reviewer"
    inject = Inject(
        id=f"{prefix}-inject-001",
        exercise_id=exercise.id,
        title=f"{exercise.name} Control Update",
        description="Mock control inject for the selected exercise workspace.",
        inject_type=InjectType.EXERCISE_CONTROL,
        priority=InjectPriority.MEDIUM,
        status=(
            InjectStatus.PENDING_REVIEW
            if exercise.status is not ExerciseStatus.ARCHIVED
            else InjectStatus.COMPLETED
        ),
        assigned_controller=controller_id,
        created_by=controller_id,
        approved_by=reviewer_id if exercise.status is ExerciseStatus.ARCHIVED else "",
    )
    registry.register_inject(inject)
    registry.register_timeline_event(
        TimelineEvent(
            id=f"{prefix}-timeline-001",
            exercise_id=exercise.id,
            event_type=TimelineEventType.EXERCISE_PHASE,
            title=f"{exercise.name} Workspace Opened",
            description="Exercise workspace seeded for Forge Studio platform context.",
            timestamp=exercise.start_date or _operation_timestamp(),
            source="forge_studio",
        )
    )
    if exercise.status is not ExerciseStatus.ARCHIVED:
        registry.register_review_item(
            StudioReviewItem(
                id=f"{prefix}-review-001",
                exercise_id=exercise.id,
                item_type=ReviewItemType.INJECT,
                item_id=inject.id,
                status=StudioReviewStatus.PENDING,
                reviewer_id=reviewer_id,
            )
        )
    registry.register_audit_log(
        AuditLog(
            id=f"{prefix}-audit-001",
            exercise_id=exercise.id,
            actor_id="user-exdir",
            action="workspace.seeded",
            target_type="exercise",
            target_id=exercise.id,
            timestamp=exercise.start_date or _operation_timestamp(),
            metadata={"status": exercise.status.value},
        )
    )


def _workspace_context_for_exercise(exercise: Exercise) -> ExerciseWorkspaceContext:
    status_label = _status_label(exercise.status.value)
    is_archived = exercise.status is ExerciseStatus.ARCHIVED
    is_active = exercise.status is ExerciseStatus.ACTIVE
    return ExerciseWorkspaceContext(
        products=[
            ExerciseProduct(
                id=f"product-{exercise.id}-summary",
                folder="Reports",
                product_type="Report",
                title=f"{exercise.name} Control Summary",
                status="Archived" if is_archived else "Draft",
                version="v1.0",
                last_updated="0830",
                author="Bridgeport EXCON" if "Mountain" in exercise.name else "Exercise Control",
                review_status="Approved" if is_archived else "Pending Review",
                metadata={"exercise": exercise.id},
                version_history=["v0.9", "v1.0"],
            ),
            ExerciseProduct(
                id=f"product-{exercise.id}-timeline",
                folder="Exports",
                product_type="Export",
                title=f"{exercise.name} Timeline Export",
                status=status_label,
                version="v0.3",
                last_updated="0815",
                author="Forge Studio",
                review_status="Logged" if is_archived else "In Review",
                metadata={"exercise": exercise.id},
                version_history=["v0.1", "v0.2", "v0.3"],
            ),
        ],
        controllers=_mock_controllers(),
        library_folders=_library_folders(),
        settings=_settings(),
        objectives=[
            f"Maintain exercise control for {exercise.name}.",
            "Preserve human review authority for all exercise products.",
            "Track decisions, injects, products, and audit records in one workspace.",
        ],
        participating_units=[
            "Exercise Control",
            "Training Audience",
            "White Cell",
            "Review Cell",
        ],
        activity=[
            {"time": "0830", "title": f"{exercise.name} Workspace Loaded"},
            {"time": "0815", "title": f"{status_label} Exercise Snapshot Updated"},
            {"time": "0800", "title": "Controller Roster Synced"},
        ],
        exercise_control="Bridgeport EXCON" if "Mountain" in exercise.name else "Exercise Control",
        exercise_director_id="user-exdir",
        training_audience="Training Audience",
        timeline_status="Archived" if is_archived else "Building" if not is_active else "On Plan",
        exercise_health="Archived" if is_archived else "Nominal",
        operational_time="0830" if not is_active else "0942",
    )


def _library_folders() -> list[str]:
    return [
        "Intelligence",
        "Injects",
        "Media",
        "Weather",
        "Reports",
        "Maps",
        "Photos",
        "Video",
        "Documents",
        "Exports",
    ]


def _settings() -> list[dict[str, str]]:
    return [
        {
            "title": "Organization",
            "description": "Organization ownership, cells, and exercise command metadata.",
        },
        {
            "title": "Exercise Defaults",
            "description": (
                "Default phase labels, timeline start, review gates, and archive policy."
            ),
        },
        {
            "title": "Appearance",
            "description": "Dark command-center theme, Forge orange accents, and density controls.",
        },
        {
            "title": "Notifications",
            "description": (
                "Review alerts, timeline changes, controller handoff, and system health."
            ),
        },
        {
            "title": "Users",
            "description": (
                "Controller roster, reviewer assignments, observers, and administrators."
            ),
        },
        {
            "title": "Integrations",
            "description": (
                "Local-only dry-run integrations reserved for future approved connectors."
            ),
        },
        {
            "title": "AI Providers",
            "description": "Offline stub configuration and future bounded provider controls.",
        },
        {
            "title": "Plugins",
            "description": "Product plugins, profile packages, and workflow module readiness.",
        },
        {
            "title": "Audit",
            "description": "Complete audit trail, activity feed retention, and export controls.",
        },
    ]


def _mock_controllers() -> list[ControllerAssignment]:
    return [
        ControllerAssignment(
            "controller-exdir",
            "Exercise Director",
            "Col Smith",
            "Commander decision point review",
            "Online",
            2,
            1,
            "user-exdir",
        ),
        ControllerAssignment(
            "controller-intel",
            "Intelligence Controller",
            "Maj Alvarez",
            "Intel update validation",
            "Online",
            4,
            1,
            "user-intel-chief",
        ),
        ControllerAssignment(
            "controller-white",
            "White Cell Controller",
            "Capt Nguyen",
            "Civilian protest inject",
            "Online",
            2,
            2,
            "user-controller",
        ),
        ControllerAssignment(
            "controller-media",
            "Media Controller",
            "Capt Brooks",
            "Media interview release",
            "Online",
            3,
            0,
            "user-media",
        ),
        ControllerAssignment(
            "controller-weather",
            "Weather Controller",
            "1stLt Pierce",
            "Avalanche warning update",
            "Online",
            2,
            0,
            "user-weather",
        ),
        ControllerAssignment(
            "controller-cyber",
            "Cyber Controller",
            "Capt Kim",
            "GPS interference inject",
            "Online",
            1,
            0,
            "user-cyber",
        ),
        ControllerAssignment(
            "controller-role-player",
            "Role Player Controller",
            "GySgt Miller",
            "Civilian protest cell",
            "Monitoring",
            0,
            0,
        ),
    ]


def _mock_products() -> list[ExerciseProduct]:
    return [
        ExerciseProduct(
            "product-intel-update-001",
            "Intelligence",
            "Intelligence",
            "Intelligence Update 001",
            "Published",
            "v1.2",
            "0937",
            "Maj Alvarez",
            "In Review",
        ),
        ExerciseProduct(
            "product-gps-interference",
            "Injects",
            "Inject",
            "GPS Interference",
            "Scheduled",
            "v1.0",
            "0935",
            "Capt Kim",
            "Approved",
        ),
        ExerciseProduct(
            "product-media-story",
            "Media",
            "Media",
            "Local Media Story",
            "Released",
            "v2.0",
            "0931",
            "Capt Brooks",
            "Approved",
        ),
        ExerciseProduct(
            "product-avalanche-warning",
            "Weather",
            "Weather",
            "Avalanche Warning",
            "Published",
            "v1.1",
            "0926",
            "1stLt Pierce",
            "Approved",
        ),
        ExerciseProduct(
            "product-blue-force-movement",
            "Reports",
            "Report",
            "Blue Force Movement Report",
            "Filed",
            "v1.0",
            "0920",
            "Capt Nguyen",
            "Logged",
        ),
        ExerciseProduct(
            "product-route-hawk",
            "Maps",
            "Map",
            "Route Hawk Overlay",
            "Current",
            "v3.4",
            "0915",
            "Bridgeport EXCON",
            "Approved",
        ),
        ExerciseProduct(
            "product-civilian-protest",
            "Injects",
            "Inject",
            "Civilian Protest Packet",
            "Pending",
            "v0.8",
            "0908",
            "Capt Nguyen",
            "Pending",
        ),
        ExerciseProduct(
            "product-drone-recon",
            "Intelligence",
            "Intelligence",
            "Drone Reconnaissance Note",
            "Published",
            "v1.0",
            "0904",
            "Maj Alvarez",
            "Approved",
        ),
        ExerciseProduct(
            "product-weather-window",
            "Weather",
            "Weather",
            "Aviation Weather Window",
            "Published",
            "v1.0",
            "0858",
            "1stLt Pierce",
            "Approved",
        ),
        ExerciseProduct(
            "product-photo-route",
            "Photos",
            "Photo",
            "Route Recon Photo Set",
            "Filed",
            "v1.0",
            "0848",
            "Role Player Cell",
            "Logged",
        ),
        ExerciseProduct(
            "product-excon-sitrep",
            "Reports",
            "Report",
            "EXCON SITREP 001",
            "Filed",
            "v1.0",
            "0835",
            "Bridgeport EXCON",
            "Logged",
        ),
        ExerciseProduct(
            "product-opening-brief",
            "Documents",
            "Document",
            "Opening Control Brief",
            "Archived",
            "v1.0",
            "0800",
            "Col Smith",
            "Approved",
        ),
    ]


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, "value"):
        return value.value
    if is_dataclass(value):
        return {key: _to_jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    return value


def _split_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).replace("\n", ";")
    return [item.strip() for item in text.split(";") if item.strip()]


def _objectives_from_titles(titles: list[str]) -> list[PlanningObjective]:
    return [
        PlanningObjective(
            id=f"objective-{index + 1:03d}",
            title=title,
            priority="Medium",
            success_criteria=["Define measurable success criteria."],
            linked_assets=[],
            status="Draft",
        )
        for index, title in enumerate(titles)
    ]


def _validation_item(label: str, issue_count: int, rule: str = "") -> dict[str, str]:
    item = {
        "label": label,
        "status": "Complete" if issue_count == 0 else f"{issue_count} warning",
        "state": "success" if issue_count == 0 else "warning",
    }
    if rule:
        item["rule"] = rule
    return item


def _next_event_titles(event_id: str, events: list[TimelineEvent]) -> list[str]:
    for index, event in enumerate(events):
        if event.id == event_id:
            return [item.title for item in events[index + 1 : index + 3]]
    return []


def _graph_node(
    node_id: str,
    name: str,
    node_type: str,
    description: str,
    exercise: str,
    status: str,
    created: str,
    modified: str,
    x: int,
    y: int,
) -> dict[str, Any]:
    return {
        "id": node_id,
        "name": name,
        "type": node_type,
        "description": description,
        "exercise": exercise,
        "status": status,
        "created": created,
        "modified": modified,
        "x": x,
        "y": y,
    }


def _required(payload: dict[str, Any], key: str) -> str:
    value = str(payload.get(key) or "").strip()
    if not value:
        raise ValueError(f"{key} is required")
    return value


def _unique_id(base: str, existing: list[str]) -> str:
    normalized = _slug(base) or "item"
    numbered_prefix = f"{normalized}-"
    numeric_suffixes = [
        int(item.removeprefix(numbered_prefix))
        for item in existing
        if item.startswith(numbered_prefix) and item.removeprefix(numbered_prefix).isdigit()
    ]
    if numeric_suffixes:
        return f"{normalized}-{max(numeric_suffixes) + 1:03d}"
    if normalized not in existing:
        return normalized
    counter = 2
    while f"{normalized}-{counter:03d}" in existing:
        counter += 1
    return f"{normalized}-{counter:03d}"


def _slug(value: str) -> str:
    cleaned = "".join(character.lower() if character.isalnum() else "-" for character in value)
    parts = [part for part in cleaned.split("-") if part]
    return "-".join(parts)


def _enum_value(enum_type: Any, value: str) -> Any:
    normalized = value.strip().lower().replace(" ", "_")
    for item in enum_type:
        if item.value == normalized or item.name.lower() == normalized:
            return item
    raise ValueError(f"unsupported {enum_type.__name__}: {value}")


def _parse_datetime(value: object) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    if not text:
        return None
    if len(text) == 4 and text.isdigit():
        return datetime(2027, 3, 27, int(text[:2]), int(text[2:]), tzinfo=timezone.utc)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _status_label(value: str) -> str:
    return value.replace("_", " ").title()


def _duration_label(start: datetime | None, end: datetime | None) -> str:
    if not start or not end:
        return "--"
    seconds = int((end - start).total_seconds())
    hours, remainder = divmod(max(seconds, 0), 3600)
    minutes = remainder // 60
    return f"{hours}h {minutes:02d}m"


def _operation_timestamp() -> datetime:
    return datetime(2027, 3, 27, 9, 43, tzinfo=timezone.utc)


def _time_label(value: datetime | None) -> str:
    if not value:
        return "--"
    return value.strftime("%H%M")
