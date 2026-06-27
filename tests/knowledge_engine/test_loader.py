from pathlib import Path

import pytest

from project_forge.knowledge_engine import (
    KnowledgeBaseLoader,
    KnowledgeDocumentType,
    load_exercise_knowledge_base,
)


def test_loader_indexes_supported_documents_by_type(tmp_path: Path) -> None:
    knowledge_base = tmp_path / "knowledge_base"
    (knowledge_base / "Road to War").mkdir(parents=True)
    (knowledge_base / "ORBAT").mkdir()
    (knowledge_base / "Training Objectives").mkdir()
    (knowledge_base / "Templates").mkdir()

    (knowledge_base / "Road to War" / "campaign.md").write_text("# Placeholder\n")
    (knowledge_base / "ORBAT" / "force-structure.yaml").write_text("placeholder: true\n")
    (knowledge_base / "Training Objectives" / "objectives.json").write_text("{}\n")
    (knowledge_base / "Templates" / "inject.docx").write_bytes(b"placeholder")
    (knowledge_base / "ignored.csv").write_text("not,indexed\n")

    exercise_kb = KnowledgeBaseLoader(knowledge_base).load(name="exercise-alpha")

    assert exercise_kb.name == "exercise-alpha"
    assert len(exercise_kb.list_documents()) == 4
    assert [
        document.relative_path.as_posix()
        for document in exercise_kb.list_documents(KnowledgeDocumentType.ROAD_TO_WAR)
    ] == ["Road to War/campaign.md"]
    assert [
        document.relative_path.as_posix()
        for document in exercise_kb.list_documents(KnowledgeDocumentType.ORBAT)
    ] == ["ORBAT/force-structure.yaml"]
    assert exercise_kb.index.document_count_by_type()[KnowledgeDocumentType.TEMPLATES] == 1


def test_loader_supports_all_required_document_categories(tmp_path: Path) -> None:
    knowledge_base = tmp_path / "knowledge_base"
    fixtures = {
        KnowledgeDocumentType.ROAD_TO_WAR: "road_to_war/history.txt",
        KnowledgeDocumentType.BASE_DOCUMENTS: "base_documents/base.md",
        KnowledgeDocumentType.COUNTRY_BOOKS: "country_books/country.yml",
        KnowledgeDocumentType.ORBAT: "orbat/order-of-battle.json",
        KnowledgeDocumentType.TRAINING_OBJECTIVES: "training_objectives/objectives.md",
        KnowledgeDocumentType.EXERCISE_TIMELINE: "exercise_timeline/timeline.yaml",
        KnowledgeDocumentType.DOCTRINE: "doctrine/manual.txt",
        KnowledgeDocumentType.TEMPLATES: "templates/template.docx",
    }

    for relative_path in fixtures.values():
        path = knowledge_base / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("placeholder\n")

    exercise_kb = load_exercise_knowledge_base(knowledge_base)

    for document_type, relative_path in fixtures.items():
        documents = exercise_kb.list_documents(document_type)
        assert [document.relative_path.as_posix() for document in documents] == [relative_path]


def test_loader_defaults_unclassified_supported_files_to_base_documents(
    tmp_path: Path,
) -> None:
    knowledge_base = tmp_path / "knowledge_base"
    knowledge_base.mkdir()
    (knowledge_base / "README.md").write_text("# Knowledge Base\n")

    exercise_kb = KnowledgeBaseLoader(knowledge_base).load()

    assert [
        document.document_type for document in exercise_kb.list_documents()
    ] == [KnowledgeDocumentType.BASE_DOCUMENTS]


def test_loader_rejects_missing_knowledge_base_path(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        KnowledgeBaseLoader(tmp_path / "missing").load()
