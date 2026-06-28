# Run Live Exercise

Use this guide to run a published Project Sentinel exercise in Forge Studio.

## Prerequisites

- The exercise has been validated in Atlas.
- The exercise has been published to Mission Control.
- The Exercise Director confirms the exercise is ready to begin.
- Required review items have a human decision or are understood as execution risks.

## Execution States

| State | Meaning |
| --- | --- |
| Not Started | Published exercise is staged but execution has not begun. |
| Running | Exercise time, inject release, timeline execution, controller updates, activity feed, audit, and analytics are active. |
| Paused | Execution is temporarily halted. |
| Completed | Exercise execution has ended and records remain available for review and AAR. |
| Archived | Exercise is closed for operational use and preserved for reference. |

## Start the Exercise

1. Open `Mission Control`.
2. Confirm the selected organization and exercise are correct.
3. Review execution status, controller status, pending reviews, active injects, upcoming timeline events, and execution alerts.
4. Select `Start Exercise`.
5. Confirm the activity feed records the start action.

Mission Control becomes the live common operational picture once execution starts.

## Manage Timeline Events

Timeline events move through:

- Pending.
- Active.
- Completed.
- Skipped.
- Delayed.

Use the Timeline workspace to:

- Activate the current event.
- Complete finished events.
- Delay events that cannot occur on schedule.
- Skip events that are intentionally omitted.
- Add execution notes for AAR and replay context.

Timeline changes update Mission Control, Analytics, Activity Feed, and Audit.

## Manage Injects

Injects move through:

- Queued.
- Released.
- Acknowledged.
- Completed.
- Returned for Revision.

Use the Inject Library to:

- Release approved injects.
- Acknowledge controller receipt.
- Complete inject execution.
- Return an inject for revision when it is not ready.

Inject release remains a human-controlled action. Forge does not automatically release injects because an item exists in the plan.

## Controller Updates

Controllers should keep their task status current.

Use the Controllers workspace to update:

- Current task.
- Status.
- Assigned inject progress.
- Upcoming event awareness.
- Notes.

These updates feed Mission Control, controller workload analytics, and the audit trail.

## Review Queue During Execution

Review decisions affect execution flow.

Use Review Queue to:

- Approve.
- Reject.
- Return for revision.
- Approve and release when a review item is tied to a releasable inject.

Human approval remains authoritative. A review decision should reflect operational judgment, not system convenience.

## Pause, Resume, End, and Archive

Use Mission Control execution controls to:

- Pause execution during a control hold.
- Resume execution after the hold is lifted.
- End execution when ENDEX is complete.
- Archive after review, AAR, and records checks are complete.

## Records Created

Every execution action creates:

- Activity feed item.
- Audit entry.
- Updated statistics.

These records support Mission Replay, AAR, regression testing, and exercise archive workflows.
