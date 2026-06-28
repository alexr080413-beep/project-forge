from __future__ import annotations

from datetime import datetime, timezone

from .models import SearchFilter, SearchIndex, SearchMatch, SearchQuery, SearchScope
from .registry import SearchRegistry


def create_sample_search_registry() -> SearchRegistry:
    """Create a sample registry with several Forge service search providers."""

    return SearchRegistry(
        indexes=[
            SearchIndex(
                identifier="knowledge",
                service="knowledge_engine",
                scope=SearchScope.KNOWLEDGE_DOCUMENTS,
                matches=[
                    SearchMatch(
                        match_id="knowledge:mwtc-weather",
                        service="knowledge_engine",
                        scope=SearchScope.KNOWLEDGE_DOCUMENTS,
                        title="MWTC Weather Notes",
                        content="Mountain weather and mobility considerations.",
                        tags=["mwtc", "weather"],
                        metadata={"profile": "mwtc"},
                        updated_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
                    )
                ],
            ),
            SearchIndex(
                identifier="events",
                service="event_engine",
                scope=SearchScope.EVENTS,
                matches=[
                    SearchMatch(
                        match_id="event:inject-001",
                        service="event_engine",
                        scope=SearchScope.EVENTS,
                        title="Mountain Mobility Inject",
                        content="A notional weather-driven route constraint.",
                        tags=["inject", "weather"],
                        metadata={"severity": "medium"},
                        updated_at=datetime(2026, 1, 3, tzinfo=timezone.utc),
                    )
                ],
            ),
        ]
    )


def create_sample_search_query() -> SearchQuery:
    """Create a deterministic partial/tag search query."""

    return SearchQuery(
        query_id="search-query-001",
        text="weather",
        filters=SearchFilter(tags=["weather"]),
        page=1,
        page_size=10,
        requested_by="EXCON",
    )
