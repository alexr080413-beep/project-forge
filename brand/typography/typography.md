# Typography

Forge typography should feel modern, operational, and readable under time pressure.

## Font Stack

| Role | Preferred | Fallback |
| --- | --- | --- |
| Headings | Space Grotesk | Inter, Segoe UI, Arial, sans-serif |
| Body | Inter | Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif |
| Monospace | JetBrains Mono | SFMono-Regular, Consolas, Liberation Mono, monospace |

## Usage

### Headings

Use Space Grotesk for brand, presentation, website, and major document headings. It gives Forge a technical but controlled voice without becoming decorative.

Fallback:

```text
Space Grotesk, Inter, Segoe UI, Arial, sans-serif
```

### Body

Use Inter for body copy, documentation, interface text, tables, and captions.

Fallback:

```text
Inter, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif
```

### Monospace

Use JetBrains Mono for:

- Event IDs
- Product IDs
- Review IDs
- Audit correlation IDs
- Timestamps
- Metrics
- Service names
- Configuration keys

Fallback:

```text
JetBrains Mono, SFMono-Regular, Consolas, Liberation Mono, monospace
```

## Hierarchy

| Level | Direction |
| --- | --- |
| Display | Use for title slides, website hero headings, and major brand moments. |
| H1 | Product name or page title. |
| H2 | Major sections such as Mission, Architecture, Messaging, Dashboard. |
| H3 | Subsections and component groups. |
| Body | Explanatory copy, documentation, and descriptions. |
| Metadata | Compact labels, IDs, timestamps, stage names, review status. |

## Rules

- Do not scale font size with viewport width.
- Keep letter spacing at `0` for body and UI text.
- Use uppercase sparingly for small labels only.
- Do not use decorative military stencil fonts.
- Do not use condensed fonts for dense tables.
- Favor short, scannable headings over slogan-heavy copy.
