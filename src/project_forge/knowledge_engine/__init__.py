"""Knowledge Engine foundation for indexing exercise knowledge documents."""

from .loader import KnowledgeBaseLoader, load_exercise_knowledge_base
from .models import (
    ExerciseKnowledgeBase,
    KnowledgeBaseIndex,
    KnowledgeDocument,
    KnowledgeDocumentType,
)

__all__ = [
    "ExerciseKnowledgeBase",
    "KnowledgeBaseIndex",
    "KnowledgeBaseLoader",
    "KnowledgeDocument",
    "KnowledgeDocumentType",
    "load_exercise_knowledge_base",
]
