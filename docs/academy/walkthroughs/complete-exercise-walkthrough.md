# Complete Exercise Walkthrough

This walkthrough uses Project Sentinel to practice Forge from planning through AAR.

Project Sentinel is the canonical Forge reference exercise for Academy, UI demonstrations, development, regression testing, documentation, screenshots, conference demonstrations, and future automated testing.

The walkthrough is intentionally scenario-based. Some actions are mock or future-facing in the current MVP, and those boundaries are called out in the relevant task guides.

## Scenario

| Field | Value |
| --- | --- |
| Organization | Marine Corps Mountain Warfare Training Center |
| Exercise | Mountain Exercise 3-27 |
| Status | Planning |
| Phase | Planning |
| Exercise Director | Colonel Smith |
| Exercise Control | Bridgeport EXCON |
| Training Audience | Infantry Battalion |
| Reference Package | [examples/sentinel](../../../examples/sentinel/README.md) |

## Walkthrough Steps

1. Create organization.
   - Use [Create Organization](../task-guides/create-organization.md) to establish the owning command or training venue.
2. Create exercise.
   - Use [Create Exercise](../task-guides/create-exercise.md) to create Mountain Exercise 3-27 from the Project Sentinel reference package.
3. Open Atlas.
   - Use the `Exercise Designer` workspace to begin planning in Atlas Alpha.
4. Add objectives.
   - Use [Sentinel objectives](../../../examples/sentinel/objectives.md) for command and control, intelligence fusion, review discipline, logistics and medical support, information environment response, and AAR evidence. Add priority, success criteria, and linked operational assets.
5. Add controllers.
   - Assign Exercise Director, Intelligence Controller, White Cell Controller, Weather Controller, Cyber Controller, and reviewers. Add responsibilities and link controllers to objectives or injects.
6. Add injects.
   - Use the [Sentinel inject library](../../../examples/sentinel/injects.md) with 50 intelligence, media, weather, cyber, medical, logistics, role player, command decision, civilian activity, and ISR injects. In Atlas Alpha, create representative injects and link each to an objective, controller, priority, notes, and planned time.
7. Link operational assets.
   - Connect objectives, injects, controllers, products, observations, and AAR findings. Confirm the Knowledge Graph updates as the exercise plan changes.
8. Validate the exercise.
   - Use [Validate Exercise](../task-guides/validate-exercise.md) to check objectives, controllers, timeline conflicts, missing relationships, and publish readiness.
9. Publish to Mission Control.
   - Use [Publish To Mission Control](../task-guides/publish-to-mission-control.md). Publishing creates a versioned Exercise Package, populates live Studio workspaces, and opens Mission Control after validation succeeds.
10. Execute the scenario.
    - Use Mission Control for the common operational picture.
11. Use Timeline.
    - Track STARTEX, intelligence baseline, weather update, injects, decision points, and ENDEX.
12. Use Inject Library.
    - Create, schedule, approve, reject, or revise injects.
13. Use Review Queue.
    - Preserve human release authority for injects and products.
14. Use Exercise Library.
    - Review products, metadata, versions, review status, and archive materials.
15. Use Knowledge Graph.
    - Inspect operational assets as connected graph nodes and relationships as graph edges.
16. Conduct AAR.
    - Trace observations and AAR findings back to objectives, timeline events, injects, and products.
17. Archive the exercise.
    - Use [Archive Exercise](../task-guides/archive-exercise.md) to close the training event and preserve records.

## Completion Criteria

You should be able to explain:

- How Forge moves from planning to execution.
- Why human review gates remain authoritative.
- How operational assets connect in Atlas and Knowledge Graph.
- How products and review records support AAR and archive.
