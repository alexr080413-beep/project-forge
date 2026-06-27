from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class KnowledgeDocumentType(str, Enum):
    """Supported exercise knowledge document categories."""

    ROAD_TO_WAR = "road_to_war"
    BASE_DOCUMENTS = "base_documents"
    COUNTRY_BOOKS = "country_books"
    ORBAT = "orbat"
    TRAINING_OBJECTIVES = "training_objectives"
    EXERCISE_TIMELINE = "exercise_timeline"
    DOCTRINE = "doctrine"
    TEMPLATES = "templates"


@dataclass(frozen=True, slots=True)
class KnowledgeDocument:
    """Filesystem metadata for a knowledge base document.

    The Knowledge Engine indexes document location and type only. It does not
    parse document bodies or inspect classified content.
    """

    path: Path
    document_type: KnowledgeDocumentType
    relative_path: Path
    suffix: str

    def __post_init__(self) -> None:
        if not str(self.path).strip():
            raise ValueError("path must not be empty")
        if not str(self.relative_path).strip():
            raise ValueError("relative_path must not be empty")
        if not self.suffix.startswith("."):
            raise ValueError("suffix must include a leading dot")


@dataclass(slots=True)
class KnowledgeBaseIndex:
    """An in-memory index of knowledge base documents."""

    root_path: Path
    documents: list[KnowledgeDocument] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not str(self.root_path).strip():
            raise ValueError("root_path must not be empty")

    def add_document(self, document: KnowledgeDocument) -> None:
        self.documents.append(document)

    def list_documents(
        self,
        document_type: KnowledgeDocumentType | None = None,
    ) -> list[KnowledgeDocument]:
        if document_type is None:
            return list(self.documents)
        return [
            document
            for document in self.documents
            if document.document_type is document_type
        ]

    def document_count_by_type(self) -> dict[KnowledgeDocumentType, int]:
        counts = {document_type: 0 for document_type in KnowledgeDocumentType}
        for document in self.documents:
            counts[document.document_type] += 1
        return counts


@dataclass(slots=True)
class ExerciseKnowledgeBase:
    """A loaded exercise knowledge base and its indexed documents."""

    root_path: Path
    index: KnowledgeBaseIndex
    name: str = "default"

    def __post_init__(self) -> None:
        if not str(self.root_path).strip():
            raise ValueError("root_path must not be empty")
        if not self.name.strip():
            raise ValueError("name must not be empty")

    def list_documents(
        self,
        document_type: KnowledgeDocumentType | None = None,
    ) -> list[KnowledgeDocument]:
        return self.index.list_documents(document_type)
