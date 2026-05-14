import pytest
from soundgate.application.use_cases.query_state import QueryStateUseCase
from soundgate.domain.aggregator import AggregatorService
from soundgate.domain.events import PlaybackState
from soundgate.domain.source import Source


def make_use_case(sources: dict) -> QueryStateUseCase:
    return QueryStateUseCase(sources=sources, aggregator=AggregatorService())


def test_active_source_returns_none_when_empty() -> None:
    assert make_use_case({}).active_source() is None


def test_active_source_returns_paused_source() -> None:
    s = Source(name="bluetooth", priority=0, state=PlaybackState.PAUSED)
    uc = make_use_case({"bluetooth": s})
    assert uc.active_source() is s


def test_all_sources_returns_copy() -> None:
    sources = {"bluetooth": Source(name="bluetooth", priority=0)}
    uc = make_use_case(sources)
    result = uc.all_sources()
    assert result == sources
    assert result is not sources
