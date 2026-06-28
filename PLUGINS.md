# Project Forge Plugins

## Product SDK

The Product SDK is the foundation for reusable Project Forge product capabilities. It defines how product plugins are described, loaded, discovered, validated, registered, and formatted.

The SDK allows the platform to support many product types without hard-coding every report into the core system.

Current Product SDK concepts include:

- `ProductMetadata`
- `ProductDefinition`
- `ProductTemplate`
- `ProductPlugin`
- `ProductOutput`
- `ProductPluginLoader`
- `ProductPluginDiscovery`
- `ProductRegistry`
- `ProductFormatter`
- `ProductValidator`

## Plugin Architecture

A product plugin is a structured definition that tells Forge:

- What the product is
- Who owns it
- Which version is active
- What product type it supports
- Which context fields are required
- Which output formats are supported
- Which template should be used
- Which fields must be supplied before formatting

The current repository stores example product plugins in `config/product_plugins/`.

## Plugin File Structure

A product plugin should include three primary sections:

### Metadata

Metadata identifies the plugin and supports discovery, ownership, and governance.

Expected fields include:

- Identifier
- Name
- Version
- Description
- Owner
- Tags
- Additional metadata

### Definition

The definition describes the product capability.

Expected fields include:

- Identifier
- Product type
- Display name
- Template identifier
- Output formats
- Required context
- Additional metadata

### Templates

Templates define reusable content structures.

Expected fields include:

- Identifier
- Version
- Content
- Required fields
- Additional metadata

## Current Report Plugins

The repository includes example plugin definitions for:

- Intelligence Summary
- Intelligence Information Report
- Social Media
- News Article
- Spot Report

These examples demonstrate how product families can be represented without implementing final report generation.

## Report Plugin Responsibilities

Report plugins should:

- Declare required context explicitly.
- Avoid embedding hidden assumptions in template text.
- Keep product ownership and version visible.
- Support deterministic formatting.
- Remain reviewable by EXCON staff.
- Preserve product type, source references, and required metadata.

Report plugins should not:

- Call external APIs directly.
- Bypass QA.
- Bypass review.
- Store secrets or private data.
- Generate final released products without controller approval.

## Future Plugin Types

The plugin model can expand beyond report templates. Future plugin types may include:

- **Source intake plugins**: Normalize news articles, official releases, social posts, or controller notes.
- **Export plugins**: Produce approved products as markdown, text, PDF, DOCX, slide decks, or other formats.
- **QA plugins**: Add venue-specific or product-specific validation checks.
- **Profile plugins**: Package scenario dictionaries, country mappings, and product preferences.
- **Review plugins**: Integrate with review queues, approval boards, or ticket systems.
- **Workflow plugins**: Provide reusable workflow definitions for product families.
- **Provider plugins**: Wrap approved AI or offline reasoning providers behind a common interface.

Future plugin types should follow the same design principle: keep capabilities explicit, versioned, testable, and reviewable.

## Plugin Governance

Plugins should be treated as controlled platform extensions.

Recommended practices:

- Use stable identifiers.
- Version every plugin.
- Keep plugin changes small.
- Validate required fields before use.
- Add tests for new plugin behavior.
- Document intended users and product families.
- Review templates for scenario consistency and release markings.
- Keep generated outputs separate from plugin definitions.

## Relationship To Profiles

Profiles select which plugins are appropriate for a given exercise context. For example, an MWTC profile may prefer mountain warfare intelligence summaries, weather impact updates, logistics injects, and safety-related controller products.

Plugins define product capability. Profiles decide when and how that capability should be used.
