"""Search Service foundation for Project Forge."""

from .examples import create_sample_search_query, create_sample_search_registry
from .models import (
    FUTURE_SEARCH_CAPABILITIES,
    SUPPORTED_SEARCH_CAPABILITIES,
    SearchFilter,
    SearchIndex,
    SearchMatch,
    SearchQuery,
    SearchResult,
    SearchScope,
)
from .registry import SearchRegistry, create_default_search_registry
from .validator import SearchValidator

__all__ = [
    "FUTURE_SEARCH_CAPABILITIES",
    "SUPPORTED_SEARCH_CAPABILITIES",
    "SearchFilter",
    "SearchIndex",
    "SearchMatch",
    "SearchQuery",
    "SearchRegistry",
    "SearchResult",
    "SearchScope",
    "SearchValidator",
    "create_default_search_registry",
    "create_sample_search_query",
    "create_sample_search_registry",
]
