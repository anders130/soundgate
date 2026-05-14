from datetime import datetime, timedelta

from soundgate.domain.aggregator import AggregatorService
from soundgate.domain.events import PlaybackState
from soundgate.domain.source import Source

NOW = datetime(2024, 1, 1, 12, 0, 0)

agg = AggregatorService(inactivity_timeout=10)


def src(name: str = "bt", priority: int = 0, **kwargs) -> Source:
    return Source(name=name, priority=priority, **kwargs)


def test_no_sources_returns_none():
    assert agg.active_source({}, NOW) is None


def test_stopped_source_is_not_candidate():
    assert agg.active_source({"bt": src()}, NOW) is None


def test_playing_within_timeout_is_active():
    s = src(state=PlaybackState.PLAYING, last_event_at=NOW)
    assert agg.active_source({"bt": s}, NOW) is s


def test_playing_beyond_timeout_is_not_active():
    s = src(state=PlaybackState.PLAYING, last_event_at=NOW - timedelta(seconds=11))
    assert agg.active_source({"bt": s}, NOW) is None


def test_paused_source_is_always_active():
    s = src(state=PlaybackState.PAUSED, last_playing_at=NOW - timedelta(days=999))
    assert agg.active_source({"bt": s}, NOW) is s


def test_lower_priority_index_wins():
    preferred = src(
        "airplay", priority=0, state=PlaybackState.PLAYING, last_event_at=NOW
    )
    other = src("bt", priority=1, state=PlaybackState.PLAYING, last_event_at=NOW)
    assert agg.active_source({"airplay": preferred, "bt": other}, NOW) is preferred


def test_same_priority_most_recently_played_wins():
    recent = src(
        "bt",
        priority=0,
        state=PlaybackState.PLAYING,
        last_event_at=NOW,
        last_playing_at=NOW,
    )
    older = src(
        "dlna",
        priority=0,
        state=PlaybackState.PLAYING,
        last_event_at=NOW,
        last_playing_at=NOW - timedelta(seconds=5),
    )
    assert agg.active_source({"bt": recent, "dlna": older}, NOW) is recent
