from datetime import datetime, timezone

import pytest

from project_forge.search_service import (
    FUTURE_SEARCH_CAPABILITIES,
    SearchFilter,
    SearchIndex,
    SearchMatch,
    SearchQuery,
    SearchRegistry,
    SearchScope,
    SearchValidator,
    create_default_search_registry,
    create_sample_search_query,
    create_sample_search_registry,
)


def match(
    match_id: str = "item-1",
    *,
    title: str = "Mountain Weather Inject",
    content: str = "A notional inject about mountain weather and mobility.",
    service: str = "event_engine",
    scope: SearchScope = SearchScope.EVENTS,
    tags: list[str] | None = None,
    metadata: dict | None = None,
    updated_at: datetime | None = None,
) -> SearchMatch:
    return SearchMatch(
        match_id=match_id,
        service=service,
        scope=scope,
        title=title,
        content=content,
        tags=tags or ["weather", "inject"],
        metadata=metadata or {"severity": "medium"},
        updated_at=updated_at or datetime(2026, 1, 2, tzinfo=timezone.utc),
    )


def index(
    identifier: str = "events",
    *,
    service: str = "event_engine",
    scope: SearchScope = SearchScope.EVENTS,
    matches: list[SearchMatch] | None = None,
) -> SearchIndex:
    return SearchIndex(
        identifier=identifier,
        service=service,
        scope=scope,
        matches=matches or [match()],
    )


def test_search_registry_supports_multiple_providers() -> None:
    registry = SearchRegistry(
        indexes=[
            index(),
            index(
                "profiles",
                service="profile_manager",
                scope=SearchScope.PROFILES,
                matches=[
                    match(
                        "profile:mwtc",
                        title="MWTC Profile",
                        content="Mountain warfare profile.",
                        service="profile_manager",
                        scope=SearchScope.PROFILES,
                        tags=["mwtc"],
                    )
                ],
            ),
        ]
    )

    assert [item.identifier for item in registry.list_indexes()] == [
        "events",
        "profiles",
    ]


def test_default_search_registry_is_empty_and_registerable() -> None:
    registry = create_default_search_registry()
    registry.register_index(index())

    assert registry.get_index("events") is not None


def test_search_query_validates_successfully() -> None:
    query = SearchQuery(query_id="query", text="weather")

    SearchValidator().validate_query(query)


def test_empty_search_query_fails_validation() -> None:
    with pytest.raises(ValueError):
        SearchValidator().validate_query(SearchQuery(query_id="query"))


def test_exact_search_ranks_exact_title_first() -> None:
    registry = SearchRegistry(
        indexes=[
            index(
                matches=[
                    match("partial", title="Mountain Weather Inject"),
                    match("exact", title="weather", content="less relevant"),
                ]
            )
        ]
    )

    result = registry.search(
        SearchQuery(query_id="query", text="weather", exact=True, partial=True)
    )

    assert [item.match_id for item in result.matches] == ["exact", "partial"]
    assert result.matches[0].score > result.matches[1].score


def test_partial_search_matches_content() -> None:
    registry = SearchRegistry(indexes=[index()])

    result = registry.search(SearchQuery(query_id="query", text="mobility"))

    assert result.total_count == 1
    assert result.matches[0].highlights


def test_tag_search_filters_and_scores() -> None:
    registry = SearchRegistry(
        indexes=[
            index(
                matches=[
                    match("weather", tags=["weather"]),
                    match("logistics", tags=["logistics"], title="Logistics Note"),
                ]
            )
        ]
    )

    result = registry.search(
        SearchQuery(query_id="query", filters=SearchFilter(tags=["weather"]))
    )

    assert [item.match_id for item in result.matches] == ["weather"]
    assert result.matches[0].score == 5


def test_metadata_search_filters_and_scores() -> None:
    registry = SearchRegistry(
        indexes=[
            index(
                matches=[
                    match("medium", metadata={"severity": "medium"}),
                    match("high", metadata={"severity": "high"}),
                ]
            )
        ]
    )

    result = registry.search(
        SearchQuery(
            query_id="query",
            filters=SearchFilter(metadata={"severity": "high"}),
        )
    )

    assert [item.match_id for item in result.matches] == ["high"]
    assert result.matches[0].score == 4


def test_date_filtering() -> None:
    registry = SearchRegistry(
        indexes=[
            index(
                matches=[
                    match("older", updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc)),
                    match("newer", updated_at=datetime(2026, 1, 4, tzinfo=timezone.utc)),
                ]
            )
        ]
    )

    result = registry.search(
        SearchQuery(
            query_id="query",
            text="weather",
            filters=SearchFilter(
                date_from=datetime(2026, 1, 3, tzinfo=timezone.utc),
            ),
        )
    )

    assert [item.match_id for item in result.matches] == ["newer"]


def test_service_and_scope_filtering() -> None:
    registry = create_sample_search_registry()

    result = registry.search(
        SearchQuery(
            query_id="query",
            text="weather",
            filters=SearchFilter(
                services=["knowledge_engine"],
                scopes=[SearchScope.KNOWLEDGE_DOCUMENTS],
            ),
        )
    )

    assert result.searched_services == ["knowledge_engine"]
    assert [item.scope for item in result.matches] == [SearchScope.KNOWLEDGE_DOCUMENTS]


def test_pagination_returns_requested_page() -> None:
    registry = SearchRegistry(
        indexes=[
            index(
                matches=[
                    match("one", title="Weather one"),
                    match("two", title="Weather two"),
                    match("three", title="Weather three"),
                ]
            )
        ]
    )

    result = registry.search(
        SearchQuery(query_id="query", text="weather", page=2, page_size=1)
    )

    assert result.total_count == 3
    assert len(result.matches) == 1
    assert result.page == 2


def test_future_semantic_vector_hybrid_capabilities_are_declared_not_implemented() -> None:
    assert FUTURE_SEARCH_CAPABILITIES == {"semantic", "vector", "hybrid"}

    with pytest.raises(NotImplementedError):
        SearchValidator().validate_query(
            SearchQuery(query_id="query", text="weather", capabilities=["semantic"])
        )


def test_all_required_scopes_are_supported() -> None:
    assert {scope.value for scope in SearchScope} == {
        "knowledge_documents",
        "events",
        "entities",
        "exercise_state",
        "scenario",
        "products",
        "review_queue",
        "qa_findings",
        "workflows",
        "profiles",
    }


def test_duplicate_indexes_are_rejected() -> None:
    item = index()

    with pytest.raises(ValueError):
        SearchRegistry(indexes=[item, item])


def test_duplicate_matches_are_rejected() -> None:
    item = match()

    with pytest.raises(ValueError):
        SearchRegistry(indexes=[index(matches=[item, item])])


def test_result_ranking_validation_rejects_unsorted_scores() -> None:
    from project_forge.search_service import SearchResult

    with pytest.raises(ValueError):
        SearchValidator().validate_result(
            SearchResult(
                query_id="query",
                matches=[
                    match("low").with_score(1, []),
                    match("high").with_score(2, []),
                ],
                total_count=2,
                page=1,
                page_size=10,
            )
        )


def test_sample_search_registry_and_query_return_ranked_results() -> None:
    registry = create_sample_search_registry()
    result = registry.search(create_sample_search_query())

    assert result.total_count == 2
    assert result.matches[0].score >= result.matches[1].score
