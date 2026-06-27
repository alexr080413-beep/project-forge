from __future__ import annotations

from pathlib import Path

from .models import (
    ExerciseKnowledgeBase,
    KnowledgeBaseIndex,
    KnowledgeDocument,
    KnowledgeDocumentType,
)


SUPPORTED_DOCUMENT_SUFFIXES = frozenset({".md", ".txt", ".yaml", ".yml", ".json", ".docx"})

_DOCUMENT_TYPE_ALIASES: dict[str, KnowledgeDocumentType] = {
    "base": KnowledgeDocumentType.BASE_DOCUMENTS,
    "base_document": KnowledgeDocumentType.BASE_DOCUMENTS,
    "base_documents": KnowledgeDocumentType.BASE_DOCUMENTS,
    "country_book": KnowledgeDocumentType.COUNTRY_BOOKS,
    "country_books": KnowledgeDocumentType.COUNTRY_BOOKS,
    "doctrine": KnowledgeDocumentType.DOCTRINE,
    "exercise_timeline": KnowledgeDocumentType.EXERCISE_TIMELINE,
    "exercise_timelines": KnowledgeDocumentType.EXERCISE_TIMELINE,
    "orbat": KnowledgeDocumentType.ORBAT,
    "orbats": KnowledgeDocumentType.ORBAT,
    "road_to_war": KnowledgeDocumentType.ROAD_TO_WAR,
    "template": KnowledgeDocumentType.TEMPLATES,
    "templates": KnowledgeDocumentType.TEMPLATES,
    "training_objective": KnowledgeDocumentType.TRAINING_OBJECTIVES,
    "training_objectives": KnowledgeDocumentType.TRAINING_OBJECTIVES,
}


class KnowledgeBaseLoader:
    """Indexes supported knowledge base files without parsing document content."""

    def __init__(self, root_path: str | Path) -> None:
        self.root_path = Path(root_path)

    def load(self, name: str = "default") -> ExerciseKnowledgeBase:
        root_path = self.root_path.resolve()
        if not root_path.exists():
            raise FileNotFoundError(f"Knowledge base path does not exist: {root_path}")
        if not root_path.is_dir():
            raise NotADirectoryError(f"Knowledge base path is not a directory: {root_path}")

        index = KnowledgeBaseIndex(root_path=root_path)
        for path in self._iter_supported_paths(root_path):
            relative_path = path.relative_to(root_path)
            document_type = self._infer_document_type(relative_path)
            index.add_document(
                KnowledgeDocument(
                    path=path,
                    document_type=document_type,
                    relative_path=relative_path,
                    suffix=path.suffix.lower(),
                )
            )

        return ExerciseKnowledgeBase(root_path=root_path, index=index, name=name)

    def _iter_supported_paths(self, root_path: Path) -> list[Path]:
        paths = [
            path
            for path in root_path.rglob("*")
            if path.is_file() and path.suffix.lower() in SUPPORTED_DOCUMENT_SUFFIXES
        ]
        return sorted(paths, key=lambda path: path.relative_to(root_path).as_posix())

    def _infer_document_type(self, relative_path: Path) -> KnowledgeDocumentType:
        for part in relative_path.parts:
            normalized = _normalize_category_name(Path(part).stem)
            if normalized in _DOCUMENT_TYPE_ALIASES:
                return _DOCUMENT_TYPE_ALIASES[normalized]
        return KnowledgeDocumentType.BASE_DOCUMENTS


def load_exercise_knowledge_base(
    root_path: str | Path = "knowledge_base",
    *,
    name: str = "default",
) -> ExerciseKnowledgeBase:
    """Load a local exercise knowledge base from filesystem metadata only."""

    return KnowledgeBaseLoader(root_path).load(name=name)


def _normalize_category_name(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")
