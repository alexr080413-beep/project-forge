# Forge Operational Knowledge Graph

The Forge Operational Knowledge Graph is the intelligence layer of Forge.

It models operational assets as graph nodes and relationships as graph edges so Forge can reason about an exercise as a connected operational system instead of isolated records.

This sprint introduces graph architecture, mock graph data, graph visualization, graph navigation, filtering, and documentation. It does not implement AI, Mission Replay, graph persistence, or graph analytics.

## Purpose

The Knowledge Graph makes the Exercise the authoritative connected model for Forge Studio.

It helps controllers and planners understand:

- Which assets support an objective.
- Which injects trigger decision points.
- Which controllers own key actions.
- Which products were produced from operational events.
- Which observations and AAR findings trace back to exercise objectives.
- Which dependencies, references, and sequencing relationships shape execution.

## Node Model

Every Operational Asset becomes a graph node.

Supported node types:

| Node Type | Description |
| --- | --- |
| Exercise | Root exercise context for the graph. |
| Objective | Training purpose, assessment anchor, and coverage target. |
| Inject | Planned or executed stimulus introduced by Exercise Control. |
| Timeline Event | Scheduled or observed event on the operational timeline. |
| Controller | Human owner, reviewer, or release authority. |
| Organization | Owning organization or exercise sponsor. |
| Unit | Training audience, participating unit, or simulated actor. |
| Product | Generated exercise product, report, artifact, or export. |
| Intelligence Update | Intelligence input or scenario-consistent update. |
| Weather Event | Environmental condition affecting operations. |
| Media Event | Simulated media, public affairs, or information event. |
| Decision Point | Commander or controller decision marker. |
| Observation | Captured observer or controller evidence. |
| AAR Finding | After-action finding tied to evidence and objectives. |
| Template | Reusable planning object inherited by exercise assets. |

Each node includes:

- Name.
- Type.
- Description.
- Exercise.
- Status.
- Connected assets.
- Relationship count.
- Created timestamp.
- Modified timestamp.

## Relationship Model

Relationships become directed graph edges.

Supported relationship types:

| Relationship | Meaning |
| --- | --- |
| `supports` | Source asset supports a target objective or outcome. |
| `produces` | Source asset produces a product, finding, or artifact. |
| `triggers` | Source asset initiates a target asset or event. |
| `depends_on` | Source asset requires the target asset or condition. |
| `assigned_to` | Source asset is assigned to a controller or role. |
| `observes` | Source asset records evidence about the target asset. |
| `evaluates` | Source asset evaluates behavior, objective performance, or evidence. |
| `references` | Source asset cites or traces to the target asset. |
| `related_to` | Source asset has a general relationship to the target asset. |
| `precedes` | Source asset occurs before the target asset. |
| `follows` | Source asset follows the target asset. |
| `contains` | Source asset owns, scopes, or contains the target asset. |
| `inherits` | Source asset provides a template or inherited structure. |

## Graph Explorer

Forge Studio includes a `Knowledge Graph` workspace.

The first graph explorer displays realistic mock graph data for Mountain Exercise 3-27. It is intentionally local and deterministic.

The workspace includes:

- Graph visualization.
- Node Inspector.
- Asset type filters.
- Search field.
- Center Graph control.
- Expand Neighbors control.
- Collapse Neighbors control.
- Relationship highlighting.

## Graph Navigation

Supported navigation behavior:

| Interaction | Behavior |
| --- | --- |
| Click node | Selects the node, highlights incoming and outgoing relationships, and updates the Node Inspector. |
| Expand neighbors | Restores the full graph view around the selected node. |
| Collapse neighbors | Dims the graph to the selected node and directly connected neighbors. |
| Center graph | Returns to the default Exercise root node and clears search/filter state. |
| Filter by asset type | Dims nodes outside the selected asset type groups. |
| Search | Dims nodes whose name, type, or description does not match the query. |
| Relationship highlighting | Emphasizes edges connected to the selected node. |

## Filtering

Initial filter groups:

- Objectives.
- Injects.
- Controllers.
- Products.
- Weather.
- Intelligence.
- Observations.
- Timeline Events.
- AAR Findings.

The filters are UI-level controls only. They do not mutate graph data.

## Mission Replay Integration

Mission Replay is not implemented in this sprint.

The Knowledge Graph prepares Replay by preserving relationships between:

- Objectives.
- Timeline events.
- Injects.
- Decision points.
- Controllers.
- Products.
- Observations.
- AAR findings.

Future Replay can use the graph to reconstruct operational threads and explain how a sequence unfolded.

## Operational Analytics Integration

Operational analytics is not implemented in this sprint.

The graph creates future analysis paths for:

- Objective coverage.
- Controller workload.
- Product generation patterns.
- Inject dependency chains.
- Timeline bottlenecks.
- Unobserved objectives.
- AAR evidence gaps.

## Future AI Usage

AI is not implemented in this sprint.

Future AI-assisted planning can use the graph as bounded context for:

- Suggesting missing relationships.
- Identifying unsupported objectives.
- Detecting unassigned injects.
- Finding weak AAR traceability.
- Surfacing dependency risks.
- Explaining why an inject or product exists.

Human judgment remains authoritative. Forge may assist; people decide.

## Future Hooks

Planned future capabilities:

- Graph analytics.
- Dependency analysis.
- Objective coverage.
- Controller workload analysis.
- Operational bottleneck detection.
- Mission Replay.
- AI reasoning.

## Current Boundaries

The current implementation does not include:

- Persistent graph storage.
- AI reasoning.
- Mission Replay.
- Graph analytics.
- Drag and drop.
- Real publishing.
- Automated recommendations.
- External data sources.
