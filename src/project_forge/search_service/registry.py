from __future__ import annotations

from dataclasses import dataclass, field

from .models import SearchIndex, SearchQuery, SearchResult
from .validator import SearchValidator


@dataclass(slots=True)
class SearchRegistry:
    """In-memory registry and query surface for search indexes."""

    indexes: list[SearchIndex] = field(default_factory=list)
    validator: SearchValidator = field(default_factory=SearchValidator)

    def __post_init__(self) -> None:
        self.validator.validate_indexes(self.indexes)
        self.indexes.sort(key=lambda index: index.identifier)

    def register_index(self, index: SearchIndex) -> None:
        if self.get_index(index.identifier) is not None:
            raise ValueError(f"search index identifier already exists: {index.identifier}")
        self.validator.validate_index(index)
        self.indexes.append(index)
        self.indexes.sort(key=lambda item: item.identifier)

    def get_index(self, identifier: str) -> SearchIndex | None:
        for index in self.indexes:
            if index.identifier == identifier:
                return index
        return None

    def list_indexes(self) -> list[SearchIndex]:
        return list(self.indexes)

    def search(self, query: SearchQuery) -> SearchResult:
        self.validator.validate_query(query)
        selected_indexes = [
            index
            for index in self.indexes
            if _index_is_selected(index, query)
        ]
        matches = []
        for index in selected_indexes:
            matches.extend(index.search(query))
        matches = sorted(matches, key=lambda match: (-match.score, match.match_id))
        start = (query.page - 1) * query.page_size
        end = start + query.page_size
        result = SearchResult(
            query_id=query.query_id,
            matches=matches[start:end],
            total_count=len(matches),
            page=query.page,
            page_size=query.page_size,
            searched_services=sorted({index.service for index in selected_indexes}),
            metadata={
                "index_count": len(selected_indexes),
                "available_future_capabilities": ["hybrid", "semantic", "vector"],
            },
        )
        self.validator.validate_result(result)
        return result


def _index_is_selected(index: SearchIndex, query: SearchQuery) -> bool:
    if query.filters.services and index.service not in query.filters.services:
        return False
    if query.filters.scopes and index.scope not in query.filters.scopes:
        return False
    return True


def create_default_search_registry() -> SearchRegistry:
    """Create an empty registry ready for multiple search providers."""

    return SearchRegistry()
