from pathlib import Path

import pytest

from project_forge.entity_engine import (
    Affiliation,
    Capability,
    EntityCatalog,
    EntityLoader,
    Individual,
    Installation,
    Organization,
    Platform,
    Relationship,
    RelationshipType,
    Unit,
    load_entities,
)


def test_entity_catalog_can_be_created_directly() -> None:
    unit = Unit(
        identifier="unit-alpha",
        display_name="Alpha Unit",
        affiliation=Affiliation.FRIENDLY,
        aliases=["AU"],
        tags=["test"],
        metadata={"source": "unit-test"},
    )
    installation = Unit(
        identifier="unit-bravo",
        display_name="Bravo Unit",
        affiliation=Affiliation.FRIENDLY,
    )
    relationship = Relationship(
        source_identifier="unit-alpha",
        target_identifier="unit-bravo",
        relationship_type=RelationshipType.SUPPORTS,
    )

    catalog = EntityCatalog(entities=[unit, installation], relationships=[relationship])

    assert catalog.get_entity("unit-alpha") is unit
    assert catalog.relationships_for("unit-alpha", RelationshipType.SUPPORTS) == [
        relationship
    ]


def test_loader_loads_example_entities() -> None:
    catalog = load_entities("config/entities.example.yaml")

    unit = catalog.get_entity("unit-jtf-hq")
    organization = catalog.get_entity("org-excon")
    installation = catalog.get_entity("inst-capital-ops")
    individual = catalog.get_entity("ind-senior-controller")
    platform = catalog.get_entity("platform-watchtower")
    capability = catalog.get_entity("cap-strategic-comms")

    assert isinstance(unit, Unit)
    assert isinstance(organization, Organization)
    assert isinstance(installation, Installation)
    assert isinstance(individual, Individual)
    assert isinstance(platform, Platform)
    assert isinstance(capability, Capability)
    assert unit.display_name == "Joint Task Force Headquarters"
    assert organization.affiliation is Affiliation.EXERCISE_CONTROL
    assert len(catalog.entities) == 6
    assert len(catalog.relationships) == 4
    assert catalog.relationships_for("unit-jtf-hq", RelationshipType.COMMANDS)


def test_relationship_rejects_self_reference() -> None:
    with pytest.raises(ValueError):
        Relationship(
            source_identifier="unit-alpha",
            target_identifier="unit-alpha",
            relationship_type=RelationshipType.SUPPORTS,
        )


def test_catalog_rejects_relationship_with_missing_entity() -> None:
    unit = Unit(
        identifier="unit-alpha",
        display_name="Alpha Unit",
        affiliation=Affiliation.FRIENDLY,
    )
    relationship = Relationship(
        source_identifier="unit-alpha",
        target_identifier="missing-unit",
        relationship_type=RelationshipType.ATTACHED_TO,
    )

    with pytest.raises(ValueError):
        EntityCatalog(entities=[unit], relationships=[relationship])


def test_all_required_relationship_types_are_supported() -> None:
    for relationship_type in RelationshipType:
        relationship = Relationship(
            source_identifier="source",
            target_identifier="target",
            relationship_type=relationship_type,
        )

        assert relationship.relationship_type is relationship_type


def test_loader_rejects_invalid_relationship_type(tmp_path: Path) -> None:
    config_path = tmp_path / "entities.yaml"
    config_path.write_text(
        """
{
  "entities": [
    {
      "identifier": "unit-alpha",
      "display_name": "Alpha Unit",
      "category": "unit",
      "affiliation": "friendly"
    },
    {
      "identifier": "unit-bravo",
      "display_name": "Bravo Unit",
      "category": "unit",
      "affiliation": "friendly"
    }
  ],
  "relationships": [
    {
      "source_identifier": "unit-alpha",
      "target_identifier": "unit-bravo",
      "relationship_type": "invalid"
    }
  ]
}
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        EntityLoader(config_path).load()
