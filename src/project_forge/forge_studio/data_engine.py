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

    @property
    def exercise_id(self) -> str:
        exercise = self._active_exercise()
        if exercise is None:
            raise ValueError("exercise store requires one active exercise")
        return exercise.id

    def snapshot(self) -> dict[str, Any]:
        """Return one JSON-ready exercise state for every application page."""

        exercise = self._required_active_exercise()
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
            "timeline.delete": self.delete_timeline_event,
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
        }
        if action not in actions:
            raise ValueError(f"unsupported action: {action}")
        return actions[action](payload)

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
        self.active_exercise_id = exercise.id
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
        if payload.get("exercise_control"):
            self.exercise_control = str(payload["exercise_control"]).strip()
        if payload.get("training_audience"):
            self.training_audience = str(payload["training_audience"]).strip()
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
        self.active_exercise_id = duplicate.id
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
        self.active_exercise_id = self.registry.exercises[0].id
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
    ) -> dict[str, Any]:
        event = TimelineEvent(
            id=f"timeline-{len(self.registry.timeline_events) + 1:03d}",
            exercise_id=self.exercise_id,
            event_type=TimelineEventType.NOTE,
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


def create_mock_exercise_store(registry: ForgeStudioRegistry | None = None) -> ExerciseStore:
    """Create the shared Exercise Data Engine for Mountain Exercise 3-27."""

    return ExerciseStore(
        registry=registry or create_mock_registry(),
        products=_mock_products(),
        controllers=_mock_controllers(),
        library_folders=[
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
        ],
        settings=[
            {
                "title": "Organization",
                "description": "Bridgeport EXCON ownership, cells, and exercise command metadata.",
            },
            {
                "title": "Exercise Defaults",
                "description": (
                    "Default phase labels, timeline start, review gates, and archive policy."
                ),
            },
            {
                "title": "Appearance",
                "description": (
                    "Dark command-center theme, Forge orange accents, and density controls."
                ),
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
                "description": (
                    "Complete audit trail, activity feed retention, and export controls."
                ),
            },
        ],
        objectives=[
            "Exercise command and control in complex mountain terrain.",
            "Evaluate intelligence-to-operations handoff under time pressure.",
            "Validate casualty evacuation and route disruption procedures.",
            "Assess media, cyber, and weather inject response.",
        ],
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
    )


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
