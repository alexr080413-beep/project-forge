from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from typing import Any

from .mock_data import create_mock_registry
from .models import (
    AuditLog,
    InjectStatus,
    ReviewDecision,
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

    @property
    def exercise_id(self) -> str:
        exercises = self.registry.list_exercises()
        if not exercises:
            raise ValueError("exercise store requires one active exercise")
        return exercises[0].id

    def snapshot(self) -> dict[str, Any]:
        """Return one JSON-ready exercise state for every application page."""

        exercise = self.registry.list_exercises()[0]
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
            "controllers": [_to_jsonable(controller) for controller in self.controllers],
            "audit_log": [self._audit_payload(log) for log in reversed(audit_logs)],
            "statistics": statistics,
        }

    def statistics(self) -> dict[str, Any]:
        """Calculate exercise statistics directly from shared state."""

        exercise = self.registry.list_exercises()[0]
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
        return self.snapshot()

    def record_timeline_event(
        self,
        *,
        title: str,
        description: str,
        source: str = "exercise_control",
        actor_id: str = "user-exdir",
    ) -> dict[str, Any]:
        event = TimelineEvent(
            id=f"timeline-{len(self.registry.timeline_events) + 1:03d}",
            exercise_id=self.exercise_id,
            event_type=TimelineEventType.NOTE,
            title=title,
            description=description,
            timestamp=_operation_timestamp(),
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
        ),
        ControllerAssignment(
            "controller-intel",
            "Intelligence Controller",
            "Maj Alvarez",
            "Intel update validation",
            "Online",
            4,
            1,
        ),
        ControllerAssignment(
            "controller-white",
            "White Cell Controller",
            "Capt Nguyen",
            "Civilian protest inject",
            "Online",
            2,
            2,
        ),
        ControllerAssignment(
            "controller-media",
            "Media Controller",
            "Capt Brooks",
            "Media interview release",
            "Online",
            3,
            0,
        ),
        ControllerAssignment(
            "controller-weather",
            "Weather Controller",
            "1stLt Pierce",
            "Avalanche warning update",
            "Online",
            2,
            0,
        ),
        ControllerAssignment(
            "controller-cyber",
            "Cyber Controller",
            "Capt Kim",
            "GPS interference inject",
            "Online",
            1,
            0,
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
