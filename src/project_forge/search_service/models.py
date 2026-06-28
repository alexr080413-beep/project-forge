from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class SearchScope(str, Enum):
    """Forge service domains that can be searched."""

    KNOWLEDGE_DOCUMENTS = "knowledge_documents"
    EVENTS = "events"
    ENTITIES = "entities"
    EXERCISE_STATE = "exercise_state"
    SCENARIO = "scenario"
    PRODUCTS = "products"
    REVIEW_QUEUE = "review_queue"
    QA_FINDINGS = "qa_findings"
    WORKFLOWS = "workflows"
    PROFILES = "profiles"


SUPPORTED_SEARCH_CAPABILITIES = {
    "exact",
    "partial",
    "tag",
    "metadata",
    "date_filter",
    "service_filter",
}
FUTURE_SEARCH_CAPABILITIES = {"semantic", "vector", "hybrid"}


@dataclass(frozen=True, slots=True)
class SearchFilter:
    """Filters applied across one or more search indexes."""

    scopes: list[SearchScope] = field(default_factory=list)
    services: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    date_from: datetime | None = None
    date_to: datetime | None = None

    def __post_init__(self) -> None:
        _validate_str_list("services", self.services)
        _validate_str_list("tags", self.tags)
        _validate_metadata(self.metadata)
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be before or equal to date_to")


@dataclass(frozen=True, slots=True)
class SearchQuery:
    """A deterministic lexical search request."""

    query_id: str
    text: str = ""
    filters: SearchFilter = field(default_factory=SearchFilter)
    exact: bool = False
    partial: bool = True
    capabilities: list[str] = field(default_factory=list)
    page: int = 1
    page_size: int = 10
    requested_by: str = "Project Forge"
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("query_id", self.query_id)
        _validate_non_empty("requested_by", self.requested_by)
        if not isinstance(self.exact, bool):
            raise ValueError("exact must be a boolean")
        if not isinstance(self.partial, bool):
            raise ValueError("partial must be a boolean")
        _validate_str_list("capabilities", self.capabilities)
        if self.page < 1:
            raise ValueError("page must be at least 1")
        if self.page_size < 1:
            raise ValueError("page_size must be at least 1")
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class SearchMatch:
    """One searchable item or ranked match."""

    match_id: str
    service: str
    scope: SearchScope
    title: str
    content: str = ""
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    score: float = 0.0
    highlights: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _validate_non_empty("match_id", self.match_id)
        _validate_non_empty("service", self.service)
        _validate_non_empty("title", self.title)
        _validate_str_list("tags", self.tags)
        _validate_metadata(self.metadata)
        if self.score < 0:
            raise ValueError("score must not be negative")
        if not all(isinstance(highlight, str) for highlight in self.highlights):
            raise ValueError("highlights must be a list of strings")

    def with_score(self, score: float, highlights: list[str]) -> SearchMatch:
        return SearchMatch(
            match_id=self.match_id,
            service=self.service,
            scope=self.scope,
            title=self.title,
            content=self.content,
            tags=list(self.tags),
            metadata=dict(self.metadata),
            created_at=self.created_at,
            updated_at=self.updated_at,
            score=score,
            highlights=highlights,
        )


@dataclass(frozen=True, slots=True)
class SearchResult:
    """Ranked, paginated search response."""

    query_id: str
    matches: list[SearchMatch]
    total_count: int
    page: int
    page_size: int
    searched_services: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("query_id", self.query_id)
        if self.total_count < 0:
            raise ValueError("total_count must not be negative")
        if self.page < 1:
            raise ValueError("page must be at least 1")
        if self.page_size < 1:
            raise ValueError("page_size must be at least 1")
        if not all(isinstance(match, SearchMatch) for match in self.matches):
            raise ValueError("matches must be a list of SearchMatch instances")
        _validate_str_list("searched_services", self.searched_services)
        _validate_metadata(self.metadata)


@dataclass(slots=True)
class SearchIndex:
    """A registerable in-memory lexical search provider."""

    identifier: str
    service: str
    scope: SearchScope
    matches: list[SearchMatch] = field(default_factory=list)
    capabilities: list[str] = field(
        default_factory=lambda: sorted(SUPPORTED_SEARCH_CAPABILITIES)
    )
    future_capabilities: list[str] = field(
        default_factory=lambda: sorted(FUTURE_SEARCH_CAPABILITIES)
    )
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("service", self.service)
        _validate_str_list("capabilities", self.capabilities)
        _validate_str_list("future_capabilities", self.future_capabilities)
        _validate_metadata(self.metadata)
        for match in self.matches:
            if match.service != self.service:
                raise ValueError("search match service must match index service")
            if match.scope is not self.scope:
                raise ValueError("search match scope must match index scope")

    def add_match(self, match: SearchMatch) -> None:
        if match.service != self.service:
            raise ValueError("search match service must match index service")
        if match.scope is not self.scope:
            raise ValueError("search match scope must match index scope")
        if any(item.match_id == match.match_id for item in self.matches):
            raise ValueError(f"search match identifier already exists: {match.match_id}")
        self.matches.append(match)

    def search(self, query: SearchQuery) -> list[SearchMatch]:
        ranked: list[SearchMatch] = []
        for match in self.matches:
            if not _passes_filters(match, query.filters):
                continue
            score, highlights = _score_match(match, query)
            if score > 0 or _filter_only_query(query):
                ranked.append(match.with_score(score, highlights))
        return sorted(ranked, key=_ranking_key)


def _passes_filters(match: SearchMatch, filters: SearchFilter) -> bool:
    if filters.scopes and match.scope not in filters.scopes:
        return False
    if filters.services and match.service not in filters.services:
        return False
    normalized_tags = {tag.lower() for tag in match.tags}
    if filters.tags and not all(tag.lower() in normalized_tags for tag in filters.tags):
        return False
    for key, expected in filters.metadata.items():
        if match.metadata.get(key) != expected:
            return False
    candidate_date = match.updated_at or match.created_at
    if filters.date_from:
        if candidate_date is None or candidate_date < filters.date_from:
            return False
    if filters.date_to:
        if candidate_date is None or candidate_date > filters.date_to:
            return False
    return True


def _score_match(match: SearchMatch, query: SearchQuery) -> tuple[float, list[str]]:
    text = query.text.strip().lower()
    score = 0.0
    highlights: list[str] = []

    if text:
        title = match.title.lower()
        content = match.content.lower()
        if query.exact:
            if text == title:
                score += 20
                highlights.append("exact title match")
            if text in content:
                score += 10
                highlights.append("exact content match")
            for key, value in match.metadata.items():
                if text == str(value).lower():
                    score += 8
                    highlights.append(f"exact metadata match: {key}")
        if query.partial:
            if text in title:
                score += 6
                highlights.append("partial title match")
            if text in content:
                score += 3 + content.count(text)
                highlights.append("partial content match")
            for key, value in match.metadata.items():
                if text in str(value).lower():
                    score += 2
                    highlights.append(f"partial metadata match: {key}")

    normalized_tags = {tag.lower() for tag in match.tags}
    for tag in query.filters.tags:
        if tag.lower() in normalized_tags:
            score += 5
            highlights.append(f"tag match: {tag}")

    for key, expected in query.filters.metadata.items():
        if match.metadata.get(key) == expected:
            score += 4
            highlights.append(f"metadata filter match: {key}")

    return score, highlights


def _filter_only_query(query: SearchQuery) -> bool:
    filters = query.filters
    return not query.text.strip() and bool(
        filters.scopes
        or filters.services
        or filters.tags
        or filters.metadata
        or filters.date_from
        or filters.date_to
    )


def _ranking_key(match: SearchMatch) -> tuple[float, datetime, str]:
    rank_date = match.updated_at or match.created_at or datetime.min.replace(tzinfo=timezone.utc)
    return (-match.score, -rank_date.timestamp(), match.match_id)


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_str_list(name: str, values: list[str]) -> None:
    if not all(isinstance(value, str) and value.strip() for value in values):
        raise ValueError(f"{name} must be a list of non-empty strings")


def _validate_metadata(metadata: dict[str, Any]) -> None:
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a dictionary")
