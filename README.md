# Forge

<p align="center">
  <img src="assets/forge-logo.png" alt="Forge metallic shield logo" width="230">
</p>

<p align="center">
  <strong>Every Event.<br>Every Inject.<br>Every Exercise.</strong>
</p>

<p align="center">
  <em>Human Command. Machine Assistance.</em>
</p>

<p align="center">
  Digital operations platform for Exercise Control.
</p>

<p align="center">
  <a href="pyproject.toml"><img alt="Python 3.11+" src="https://img.shields.io/badge/python-3.11%2B-202A33"></a>
  <a href="LICENSE"><img alt="License MIT" src="https://img.shields.io/badge/license-MIT-6F7C86"></a>
  <a href="tests"><img alt="Tests Pytest" src="https://img.shields.io/badge/tests-pytest-D6A84F"></a>
  <a href="WORKFLOWS.md"><img alt="Local deterministic foundation" src="https://img.shields.io/badge/runtime-local%20deterministic-F97316"></a>
  <a href="SECURITY.md"><img alt="No external calls by default" src="https://img.shields.io/badge/external%20calls-none%20by%20default-0B0F14"></a>
</p>

Forge is a digital operations platform for Exercise Control.

Forge is a modular Exercise Intelligence and Control Platform designed to transform real-world information into scenario-consistent training products through deterministic services, AI-assisted reasoning, and human-controlled workflows.

Forge gives Exercise Control teams a disciplined path from signal to scenario-safe product: source context, scenario grounding, translation, reasoning support, quality checks, human review, dry-run distribution, audit traceability, and operational metrics.

## Brand Identity

Forge uses a dark metallic command-center identity built around disciplined control, operational confidence, and machine-assisted production under human authority.

| Element | Direction |
| --- | --- |
| Product name | Forge |
| Description | Digital operations platform for Exercise Control. |
| Logo concept | Metallic shield with an integrated anvil base and abstract forged `F` mark, lit by a restrained orange forge glow. |
| Slogan | Every Event. Every Inject. Every Exercise. |
| Tagline | Human Command. Machine Assistance. |
| Visual posture | Military, enterprise, command-center, precise, durable, and audit-ready. |

### Color Palette

| Token | Hex | Use |
| --- | --- | --- |
| Command Black | `#0B0F14` | Primary background and dark surfaces. |
| Gunmetal | `#202A33` | Logo depth, panels, structural UI, and secondary badges. |
| Steel | `#6F7C86` | Metallic highlights, separators, and neutral interface states. |
| Forge Orange | `#F97316` | Primary brand energy, active accents, and forge glow. |
| Ember Amber | `#D6A84F` | Review, caution, warmth, and supporting highlights. |
| Signal White | `#E6EDF3` | Primary text, logo edge highlights, and high-contrast foregrounds. |

### Typography Direction

Forge should use strong, readable enterprise typography: a modern sans-serif for interface and documentation surfaces, paired with a compact monospace for identifiers, audit records, timestamps, metrics, event IDs, and service names.

### Design Principles

- Lead with the mark, slogan, and tagline before technical detail.
- Preserve a dark command-center appearance without turning the brand into decoration.
- Use orange glow as a controlled signal of forge energy, not as a dominant background.
- Keep language direct, operational, and human-authority centered.
- Avoid consumer-app softness, playful illustration, uncontrolled gradients, and decorative clutter.

## Mission

Forge exists to help Exercise Control teams rapidly convert fast-moving real-world signals into credible, notional exercise products while preserving scenario fidelity, source traceability, editorial control, and clear fiction boundaries.

The platform is built around one operational question:

> What would this real-world signal look like inside our exercise world?

## Vision

Forge is intended to become the control framework for AI-assisted exercise production. It separates intake, scenario context, deterministic translation, bounded reasoning, product preparation, quality assurance, review authority, distribution handling, audit logging, metrics, configuration, automation, and security into explicit platform services.

The desired end state is faster controller production, stronger scenario discipline, reusable exercise profiles, governed product plugins, and auditable workflows that leadership, controllers, and developers can understand.

## Core Principles

| Principle | Meaning |
| --- | --- |
| Scenario fidelity first | Products must conform to approved exercise facts, entities, timelines, assumptions, constraints, and objectives. |
| Human release authority | Forge can assist preparation, validation, and drafting, but controllers remain the approval authority. |
| Deterministic foundations | Local services validate, transform, and route data predictably before any future live integrations are introduced. |
| Source traceability | Products retain enough source, context, and transformation metadata to explain why they exist. |
| Clear fiction boundaries | Real-world material and notional exercise truth remain visibly separated. |
| Modular service design | Each capability owns a narrow responsibility and can be tested independently. |
| Audit-ready operations | Decisions, reviews, distributions, configurations, and workflow execution are structured for after-action review. |

## Platform Architecture

```mermaid
flowchart LR
    A["Real-World Signal"] --> B["Integration Service<br/>dry-run intake"]
    B --> C["Storage Service<br/>artifact boundary"]
    C --> D["Scenario Context Layer"]
    D --> E["Translation Engine"]
    E --> F["AI Reasoning Engine<br/>offline stub today"]
    F --> G["Product SDK"]
    G --> H["QA Service"]
    H --> I["Review Queue"]
    I --> J["Distribution Service<br/>dry-run or local"]
    J --> K["Approved Exercise Output"]

    L["Knowledge Engine"] --> D
    M["Scenario Engine"] --> D
    N["Entity Engine"] --> D
    O["Event Engine"] --> D
    P["Decision Engine"] --> D
    Q["Exercise State Engine"] --> D

    R["Audit Service"] -. "records" .-> B
    R -. "records" .-> I
    R -. "records" .-> J
    S["Metrics Service"] -. "observes" .-> G
    S -. "observes" .-> H
    S -. "observes" .-> J
```

```mermaid
flowchart TB
    subgraph "Source And Event"
        integration["Integration Service"]
        event["Event Engine"]
        storage["Storage Service"]
    end

    subgraph "Scenario Context"
        knowledge["Knowledge Engine"]
        scenario["Scenario Engine"]
        entity["Entity Engine"]
        exercise_state["Exercise State Engine"]
        decision["Decision Engine"]
        context["Context Engine"]
    end

    subgraph "Preparation"
        profile["Profile Manager"]
        translation["Translation Engine"]
        ai["AI Reasoning Engine"]
        product["Product SDK"]
    end

    subgraph "Control And Release"
        qa["QA Service"]
        review["Review Queue"]
        distribution["Distribution Service"]
    end

    subgraph "Operations"
        workflow["Workflow Engine"]
        pipeline["Pipeline Orchestrator"]
        automation["Automation Service"]
        search["Search Service"]
        audit["Audit Service"]
        metrics["Metrics Service"]
        config["Configuration Service"]
        security["Security Service"]
    end

    integration --> event --> context
    storage --> context
    knowledge --> context
    scenario --> context
    entity --> context
    exercise_state --> context
    decision --> context
    profile --> translation --> ai --> product --> qa --> review --> distribution
    context --> translation
    pipeline --> integration
    pipeline --> context
    pipeline --> product
    workflow --> pipeline
    automation --> workflow
    config --> pipeline
    security --> pipeline
    audit --> pipeline
    metrics --> pipeline
    search --> context
```

## Domains

Forge is organized into operational domains that map to controller workflows and software ownership boundaries.

| Domain | Purpose | Primary Modules |
| --- | --- | --- |
| Source and event intake | Represent signals, dry-run integrations, source metadata, and exercise events. | Integration Service, Event Engine, Storage Service |
| Scenario context | Maintain exercise truth, current state, entities, knowledge, and decision inputs. | Knowledge Engine, Scenario Engine, Entity Engine, Exercise State Engine, Decision Engine, Context Engine |
| Translation and profiles | Adapt real-world terminology into controlled exercise language. | Profile Manager, Translation Engine |
| Reasoning and product preparation | Build bounded reasoning requests and format draft products from validated context. | AI Reasoning Engine, Product SDK |
| Quality and review | Validate products and hold them for human control before release. | QA Service, Review Queue, Distribution Service |
| Platform operations | Coordinate, observe, search, audit, configure, automate, and secure local workflows. | Pipeline Orchestrator, Workflow Engine, Automation Service, Search Service, Audit Service, Metrics Service, Configuration Service, Security Service |

## Services

| Service | Responsibility | Status |
| --- | --- | --- |
| Core Models | Shared source, scenario, report, review, and quality containers. | Implemented foundation |
| Integration Service | Source definitions, connector registration, validation, dry-run collection, and audit metadata. | Implemented foundation |
| Knowledge Engine | Local knowledge document indexing and references. | Implemented foundation |
| Scenario Engine | Scenario facts, assumptions, constraints, objectives, control measures, status, and tempo. | Implemented foundation |
| Entity Engine | Exercise organizations, units, installations, individuals, platforms, capabilities, and relationships. | Implemented foundation |
| Event Engine | Exercise events, severity, impacts, status, entities, locations, and source references. | Implemented foundation |
| Exercise State Engine | Current phase, exercise day, tempo, escalation, and situation state. | Implemented foundation |
| Context Engine | Deterministic context snapshots across scenario, state, entities, events, decisions, and knowledge. | Implemented foundation |
| Decision Engine | Deterministic rules for escalation, training objective relevance, duplicates, and consistency. | Implemented foundation |
| Profile Manager | Exercise profiles that select services, plugins, dictionaries, workflows, and paths. | Implemented foundation |
| Translation Engine | Deterministic dictionaries, aliases, regex rules, profiles, and translation results. | Implemented foundation |
| AI Reasoning Engine | Prompt building and provider interfaces with offline stub support and no live API calls. | Implemented foundation |
| Product SDK | Product plugin loading, discovery, validation, registry support, and deterministic formatting. | Implemented foundation |
| QA Service | Required metadata checks, source traceability, confidence warnings, and leakage checks. | Implemented foundation |
| Review Queue | Human review items, assignment, approval, rejection, revisions, notes, and audit history. | Implemented foundation |
| Distribution Service | Approved-output handling with dry-run, local, archive, and placeholder channels. | Implemented foundation |
| Storage Service | Local and placeholder storage providers, metadata reads, dry-run writes, listing, and archive handling. | Implemented foundation |
| Search Service | Deterministic local search indexes, filters, ranking, pagination, and future semantic capability declarations. | Implemented foundation |
| Audit Service | In-memory audit events, sessions, categories, actions, severities, tags, metadata, and filtering. | Implemented foundation |
| Metrics Service | Counters, gauges, timers, snapshots, reports, collectors, tags, and standard operational metrics. | Implemented foundation |
| Configuration Service | YAML/JSON settings, scopes, profiles, defaults, precedence, env placeholders, and change records. | Implemented foundation |
| Automation Service | Schedule, manual, event, workflow, and conditional trigger recording without external schedulers. | Implemented foundation |
| Security Service | Principals, roles, permissions, policies, RBAC decisions, validation, and audit-ready records. | Implemented foundation |
| Demo Pipeline | End-to-end sample workflow across implemented local services. | Implemented foundation |
| Workflow Engine | Ordered local workflow definitions, conditions, retries, execution logs, and results. | Implemented foundation |
| Pipeline Orchestrator | Ordered service pipelines with stage results, context propagation, metadata, logs, and failure handling. | Implemented foundation |

For service-level inputs, outputs, dependencies, and boundaries, see [SERVICES.md](SERVICES.md).

## Forge Modules

Forge modules are the future packaging boundary for reusable operational capability.

| Module Type | Intent | Current Position |
| --- | --- | --- |
| Source modules | Normalize source families such as public releases, controller notes, social narratives, or local files. | Placeholder |
| Profile modules | Package exercise environment rules, scenario mappings, terminology, and product preferences. | Placeholder |
| Product modules | Provide governed product definitions, templates, required context, and output formats. | Product SDK foundation exists |
| QA modules | Add venue-specific, scenario-specific, or product-specific validation checks. | Placeholder |
| Export modules | Produce approved outputs in document, briefing, markdown, text, or archive formats. | Placeholder |
| Provider modules | Wrap approved AI or offline reasoning providers behind common interfaces. | Provider interface foundation exists |
| Workflow modules | Package reusable controller workflows for daily summaries, injects, white cell products, and reporting sequences. | Workflow foundation exists |

## Profiles

Profiles adapt Forge to a training venue, exercise family, unit, or operating environment without modifying Forge Core.

Current profile foundations support:

- Profile identifier, display name, owner, version, and metadata
- Enabled services and plugins
- Knowledge base, template, translation dictionary, and workflow paths
- Default scenario selection
- Profile components for dictionaries, templates, workflows, and future controlled artifacts

Example profile direction includes MWTC, ITX, and Joint Exercise environments. Profile governance should treat country mappings, actor mappings, escalation boundaries, and release rules as controlled exercise policy.

See [PROFILES.md](PROFILES.md) for profile concepts, MWTC direction, translation dictionaries, country mappings, and governance notes.

## Plugins

Plugins define reusable product capabilities without hard-coding every report family into the core platform.

Current product plugin examples include:

- Intelligence Summary
- Intelligence Information Report
- Social Media
- News Article
- Spot Report

Each product plugin declares metadata, product type, required context, supported formats, templates, required fields, ownership, version, and governance metadata. Plugins are deterministic, reviewable, and designed to remain behind QA and human review.

See [PLUGINS.md](PLUGINS.md) and [`config/product_plugins/`](config/product_plugins/) for the current plugin model and examples.

## Run The Demo

Forge includes a full local demonstration pipeline that exercises the completed foundation architecture without external calls.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m project_forge.demo_pipeline
```

Run the local Forge Studio Web MVP with:

```bash
python -m project_forge.forge_studio.web_app
```

Then open `http://127.0.0.1:8765`.

Expected result:

```text
Pipeline: forge-core-demo
Status: succeeded
- sample-real-world-event: succeeded (source_intake)
- integration-dry-run: succeeded (integration_service)
- storage: succeeded (storage_service)
- knowledge-lookup: succeeded (knowledge_engine)
- scenario-lookup: succeeded (scenario_engine)
- entity-lookup: succeeded (entity_engine)
- event-creation: succeeded (event_engine)
- decision-engine: succeeded (decision_engine)
- context-engine: succeeded (context_engine)
- translation-engine: succeeded (translation_engine)
- ai-reasoning-stub: succeeded (ai_reasoning_engine)
- product-sdk: succeeded (product_sdk)
- qa-service: succeeded (qa_service)
- review-queue: succeeded (review_queue)
- distribution-dry-run: succeeded (distribution_service)
- audit-log: succeeded (audit_service)
- metrics-snapshot: succeeded (metrics_service)
```

The demo uses repository sample data, dry-run handlers, and the offline AI stub provider. It does not call external APIs, invoke OpenAI, send email, scrape websites, or publish products.

## Roadmap

| Phase | Focus |
| --- | --- |
| Phase 0: Foundation | Repository structure, documentation, package layout, test scaffold, local service foundations, and current demo pipeline. |
| Phase 1: First Capability | Define the first controller-facing workflow, strengthen sample data, and make end-to-end behavior easier to operate. |
| Phase 2: Quality Baseline | Expand automated tests, add linting and formatting commands, type checking, and meaningful CI checks. |
| Phase 3: Operations | Define release processes, generated-output retention, runbook procedures, and runtime observability guidance. |
| Future Product Growth | Add production-grade user interfaces, persistent storage, approved integrations, richer export support, and governed provider modules. |

See [ROADMAP.md](ROADMAP.md) for the lightweight roadmap and [WORKFLOWS.md](WORKFLOWS.md) for workflow direction.

## Current Status

Forge is a local, deterministic platform foundation. The repository now contains typed domain models, service registries, validators, loaders, sample configuration, product plugins, and an end-to-end demo pipeline.

Current boundaries:

- No real OpenAI or live AI provider calls
- No web scraping
- No email, SharePoint, Teams, or social media access
- No external identity provider or CAC integration
- No persistent database
- No automatic release of products into exercise play

The platform is ready for iterative capability growth while preserving controller authority, scenario fidelity, and auditability.

## Repository Layout

```text
.
├── assets/                # Logo and static project assets
├── brand/                 # Official Forge brand kit, messaging, visual system, and marketing guidance
├── config/                # Safe sample configuration, profiles, workflows, dictionaries, plugins
├── design_system/         # Forge Studio reusable UI components, tokens, and usage guidance
├── docs/                  # Forge Academy, vision docs, documentation policy, and prompts
├── examples/              # Safe notional exercise examples
├── knowledge_base/        # Durable exercise knowledge references
├── outputs/               # Local generated artifacts, ignored except placeholders
├── src/project_forge/     # Forge Python package and service foundations
├── tests/                 # Unit and integration tests mirroring package structure
├── ARCHITECTURE.md        # Design boundaries and architecture notes
├── PLATFORM.md            # Platform layers, data flow, and core concepts
├── EXERCISE.md            # Exercise lifecycle model and Forge Studio organizing concept
├── SERVICES.md            # Service responsibilities and boundaries
├── WORKFLOWS.md           # Workflow philosophy and demo pipeline
├── FORGE_STUDIO_UX.md     # UX blueprint for the future Forge Studio application
├── FORGE_STUDIO_MVP.md    # Forge Studio MVP domain model and API foundation
├── FORGE_STUDIO_WEB.md    # Runnable local Forge Studio Web MVP
├── FORGE_STUDIO_WORKSPACE_FRAMEWORK.md # Organization, exercise, workspace navigation model
├── FORGE_STUDIO_EXERCISE_DESIGNER.md # Project Atlas Exercise Designer framework
├── FORGE_OPERATIONAL_KNOWLEDGE_GRAPH.md # Operational Knowledge Graph model
├── FORGE_STUDIO_DESIGN_SYSTEM.md # Forge Studio design system
├── FORGE_STUDIO_MISSION_CONTROL.md # Mission Control dashboard specification
├── FORGE_STUDIO_INTELLIGENCE_WORKSPACE.md # Intelligence Controller workspace specification
├── PROFILES.md            # Profile model and governance
├── PLUGINS.md             # Product SDK and plugin model
├── DEVELOPMENT.md         # Coding, testing, milestone, and contribution standards
├── SETUP.md               # Local setup and validation commands
├── RUNBOOK.md             # Operational maintenance notes
├── SECURITY.md            # Security reporting and sensitive-data guidance
├── CHANGELOG.md           # Human-readable change history
└── pyproject.toml         # Python project metadata and tooling configuration
```

## Documentation

| Document | Purpose |
| --- | --- |
| [brand/README.md](brand/README.md) | Official Forge brand kit covering identity, messaging, voice, logo, colors, typography, icons, imagery, UI guidance, and presentations. |
| [design_system/README.md](design_system/README.md) | Forge Studio reusable UI components, tokens, usage examples, accessibility rules, responsive guidance, and runtime implementation contract. |
| [docs/academy/README.md](docs/academy/README.md) | Forge Academy training system with role-based learning paths, walkthroughs, lessons, task guides, troubleshooting, and reference material. |
| [docs/DOCUMENTATION_POLICY.md](docs/DOCUMENTATION_POLICY.md) | Documentation policy requiring workflow, setup, API, plugin, data model, and architecture changes to update relevant docs. |
| [docs/prompts/codex-ticket-template.md](docs/prompts/codex-ticket-template.md) | Standard Codex ticket template with documentation, testing, human-in-the-loop, security, and no-go constraint sections. |
| [docs/governance/CONTRIBUTING.md](docs/governance/CONTRIBUTING.md) | Governance contribution workflow, branch naming, issue process, pull request process, and review expectations. |
| [docs/governance/ENGINEERING_STANDARDS.md](docs/governance/ENGINEERING_STANDARDS.md) | Engineering standards, documentation expectations, UI consistency, accessibility, security, human review, and permanent Codex prompt policy. |
| [docs/governance/DEFINITION_OF_DONE.md](docs/governance/DEFINITION_OF_DONE.md) | Definition of Done checklist for implementation, tests, documentation, Academy, ADRs, RFCs, changelog, and screenshots. |
| [docs/decisions/README.md](docs/decisions/README.md) | Architecture Decision Record process, lifecycle, template, and initial decision register. |
| [docs/rfcs/README.md](docs/rfcs/README.md) | RFC proposal lifecycle, statuses, review expectations, and template. |
| [docs/releases/CHANGELOG.md](docs/releases/CHANGELOG.md) | Keep-a-Changelog style release history beginning with v0.1.0 Foundation Release. |
| [examples/README.md](examples/README.md) | Safe sample exercise documentation for Mountain Exercise 3-27, humanitarian assistance, information warfare, island chain defense, and arctic operations. |
| [examples/sentinel/README.md](examples/sentinel/README.md) | Project Sentinel, the canonical Forge reference exercise for Academy, UI demonstrations, development, regression testing, documentation, screenshots, and conference demonstrations. |
| [VISION.md](VISION.md) | Executive vision, problem statement, goals, non-goals, and EXCON benefits. |
| [PLATFORM.md](PLATFORM.md) | Platform layers, architecture, data flow, and core concepts. |
| [EXERCISE.md](EXERCISE.md) | Exercise lifecycle model, object model, hierarchy, workspace mapping, controller mapping, workflow mapping, product mapping, profile mapping, plugin mapping, and navigation implications. |
| [SERVICES.md](SERVICES.md) | Service responsibilities, inputs, outputs, dependencies, status, and boundaries. |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Architecture notes and foundation design boundaries. |
| [WORKFLOWS.md](WORKFLOWS.md) | Workflow philosophy, demo pipeline, and future workflow direction. |
| [FORGE_STUDIO_UX.md](FORGE_STUDIO_UX.md) | User personas, workspaces, navigation, workflows, wireframes, and accessibility guidance for Forge Studio. |
| [FORGE_STUDIO_MVP.md](FORGE_STUDIO_MVP.md) | Forge Studio MVP domain objects, object relationships, API module purpose, and human-in-the-loop review principle. |
| [FORGE_STUDIO_WEB.md](FORGE_STUDIO_WEB.md) | Local runnable Forge Studio Web MVP, Exercise Workspace, Exercise Library, start command, dashboard behavior, structure, and boundaries. |
| [FORGE_STUDIO_WORKSPACE_FRAMEWORK.md](FORGE_STUDIO_WORKSPACE_FRAMEWORK.md) | Permanent Forge Studio hierarchy, organization model, exercise workspace model, navigation philosophy, workspace philosophy, command palette vision, and global search direction. |
| [FORGE_STUDIO_EXERCISE_DESIGNER.md](FORGE_STUDIO_EXERCISE_DESIGNER.md) | Project Atlas planning workspace, Exercise Designer purpose, relationship engine, exercise graph, design-validate-publish-execute lifecycle, planned-to-live object mapping, and human approval principle. |
| [FORGE_OPERATIONAL_KNOWLEDGE_GRAPH.md](FORGE_OPERATIONAL_KNOWLEDGE_GRAPH.md) | Operational Knowledge Graph node model, relationship model, graph navigation, filters, future AI usage, Mission Replay integration, and operational analytics hooks. |
| [FORGE_STUDIO_DESIGN_SYSTEM.md](FORGE_STUDIO_DESIGN_SYSTEM.md) | Brand identity, visual tokens, layout rules, component specifications, themes, and UI states for Forge Studio. |
| [FORGE_STUDIO_MISSION_CONTROL.md](FORGE_STUDIO_MISSION_CONTROL.md) | Mission Control dashboard purpose, layout, widgets, interactions, refresh behavior, and operational rules. |
| [FORGE_STUDIO_INTELLIGENCE_WORKSPACE.md](FORGE_STUDIO_INTELLIGENCE_WORKSPACE.md) | Intelligence Controller workspace workflow, panels, shortcuts, collaboration, search, and performance specification. |
| [PROFILES.md](PROFILES.md) | Profile concepts, MWTC direction, dictionaries, mappings, and governance. |
| [PLUGINS.md](PLUGINS.md) | Product SDK, plugin architecture, report plugins, and future plugin types. |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Coding standards, test standards, ticket conventions, and review expectations. |
| [SETUP.md](SETUP.md) | Local development setup and validation commands. |
| [RUNBOOK.md](RUNBOOK.md) | Maintainer operations and future incident/release placeholders. |
| [SECURITY.md](SECURITY.md) | Vulnerability reporting and sensitive-data handling. |
| [CHANGELOG.md](CHANGELOG.md) | Notable changes. |

## Contributing

Forge is built for disciplined, reviewable platform growth.

Recommended workflow:

1. Read the relevant repository documentation.
2. Keep changes focused on a single service boundary or workflow.
3. Add focused tests for behavior changes.
4. Preserve deterministic local behavior and avoid hidden external calls.
5. Update documentation when architecture, services, workflows, configuration, profiles, plugins, or operations change.
6. Run the test suite before handoff.

```bash
python -m pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) and [DEVELOPMENT.md](DEVELOPMENT.md) for expectations.

## License

Forge is released under the [MIT License](LICENSE).
