from __future__ import annotations

from .models import (
    FUTURE_SEARCH_CAPABILITIES,
    SUPPORTED_SEARCH_CAPABILITIES,
    SearchIndex,
    SearchQuery,
    SearchResult,
)


class SearchValidator:
    """Validates search indexes, queries, and results."""

    def validate_index(self, index: SearchIndex) -> None:
        unknown = set(index.capabilities) - SUPPORTED_SEARCH_CAPABILITIES
        if unknown:
            raise ValueError(f"unsupported search capabilities: {sorted(unknown)}")
        future_unknown = set(index.future_capabilities) - FUTURE_SEARCH_CAPABILITIES
        if future_unknown:
            raise ValueError(f"unknown future search capabilities: {sorted(future_unknown)}")
        identifiers = [match.match_id for match in index.matches]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("search match identifiers must be unique within an index")

    def validate_indexes(self, indexes: list[SearchIndex]) -> None:
        identifiers = [index.identifier for index in indexes]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("search index identifiers must be unique")
        for index in indexes:
            self.validate_index(index)

    def validate_query(self, query: SearchQuery) -> None:
        if not query.text.strip() and not (
            query.filters.scopes
            or query.filters.services
            or query.filters.tags
            or query.filters.metadata
            or query.filters.date_from
            or query.filters.date_to
        ):
            raise ValueError("search query must include text or at least one filter")
        requested = set(query.capabilities)
        future = requested & FUTURE_SEARCH_CAPABILITIES
        if future:
            raise NotImplementedError(
                f"future search capabilities are not implemented: {sorted(future)}"
            )
        unknown = requested - SUPPORTED_SEARCH_CAPABILITIES
        if unknown:
            raise ValueError(f"unsupported search capabilities: {sorted(unknown)}")

    def validate_result(self, result: SearchResult) -> None:
        if result.total_count < len(result.matches):
            raise ValueError("total_count must be greater than or equal to returned matches")
        scores = [match.score for match in result.matches]
        if scores != sorted(scores, reverse=True):
            raise ValueError("search results must be ranked by descending score")
