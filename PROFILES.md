# Project Forge Profiles

## Profile Concept

A Project Forge profile packages the exercise-specific rules that make platform output credible for a particular venue, training audience, scenario family, or operating environment.

Profiles answer questions such as:

- What fictional countries, organizations, units, and locations replace real-world terms?
- Which entities are approved for the scenario?
- Which terminology should never appear in released exercise products?
- Which report types are preferred for the exercise?
- Which control measures, approval rules, and confidence expectations apply?
- Which translation dictionaries and country mappings should be active?

Profiles allow Project Forge to remain a reusable platform while adapting to local exercise needs.

## Profile Contents

A mature profile should include:

- Profile identifier, name, owner, and version
- Exercise or venue description
- Scenario assumptions and boundaries
- Country mappings
- Organization and unit mappings
- Location mappings
- Political leader and role mappings
- Equipment and platform mappings
- Translation dictionaries
- Product plugin preferences
- QA policy settings
- Review and release rules
- Metadata for audit and governance

## MWTC Profile

The Marine Corps Mountain Warfare Training Center (MWTC) profile should represent a mountain warfare training environment with scenario-specific geography, weather, logistics, command relationships, adversary or partner entities, and exercise control rules.

An MWTC profile would likely include:

- Mountain training area terminology
- Cold weather and high-altitude operational context
- Notional local government and host-nation mappings
- Friendly, adversary, neutral, and exercise-control entities
- Mountain mobility, sustainment, casualty evacuation, communications, and weather impacts
- Product types tailored to controller injects, intelligence summaries, logistics updates, media simulation, and command decision support
- QA rules for training safety, escalation control, and fiction boundaries

The MWTC profile should make it possible to transform a real-world signal into a notional event that feels natural inside a mountain warfare exercise without importing unsupported real-world geopolitical details.

## Future Profile Examples

Future profiles may include:

- **Large-scale combat operations profile**: Focused on corps or division-level maneuver, joint fires, sustainment, information operations, and escalation control.
- **Humanitarian assistance and disaster response profile**: Focused on civil authorities, relief agencies, infrastructure damage, population movement, and public information.
- **Maritime security profile**: Focused on port operations, maritime interdiction, territorial waters, shipping, and partner nation coordination.
- **Cyber defense profile**: Focused on network events, public attribution rules, incident response, infrastructure impacts, and information environment effects.
- **Urban operations profile**: Focused on municipal actors, dense infrastructure, public safety, media pressure, and civilian movement.
- **Joint information environment profile**: Focused on social media narratives, press releases, public affairs, adversary messaging, and rumor control.

Each profile should remain explicit about what is scenario truth, what is source material, and what is not authorized for release.

## Translation Dictionaries

Translation dictionaries are deterministic rule sets that convert real-world or generic exercise terms into scenario-specific language.

Current dictionary categories include:

- Countries
- Military organizations
- Units
- Geographic locations
- Political leaders
- Military equipment
- Government agencies
- Alliances
- Exercises

Rules may support:

- One-to-one replacement
- Alias replacement
- Regular expression replacement
- Priority ordering
- Case handling
- Metadata for audit and review

Example:

```text
Host Nation -> Asteria
Joint Task Force -> Combined Response Group
Capital Operations Center -> Asteria Coordination Center
```

Translation dictionaries should be deterministic, reviewable, and versioned with the profile.

## Country Mappings

Country mappings define how real-world countries, regions, alliances, and political entities are represented in the exercise world.

A country mapping should define:

- Source country or region
- Notional country or region
- Approved aliases
- Relationship to exercise factions or scenario actors
- Sensitivity notes
- Disallowed terms
- Confidence or review requirements

Country mappings are especially important because they protect fiction boundaries and reduce the risk of accidental real-world attribution.

## Profile Governance

Profiles should be controlled artifacts. Changes to profile mappings can materially change exercise meaning, so updates should be reviewed like code.

Recommended governance:

- Keep profile changes small and traceable.
- Require review for country, actor, and escalation-sensitive mappings.
- Test dictionaries against representative products.
- Record why a mapping exists.
- Avoid embedding secrets, private data, or operationally sensitive details.
- Treat profiles as exercise control policy, not just configuration.
