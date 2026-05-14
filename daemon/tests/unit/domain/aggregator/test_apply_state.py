from datetime import datetime, timedelta

from soundgate.domain.aggregator import AggregatorService
from soundgate.domain.events import PlaybackState
from soundgate.domain.source import Source

NOW = datetime(2024, 1, 1, 12, 0, 0)

agg = AggregatorService(inactivity_timeout=10)


def src(**kwargs) -> Source:
    return Source(name="bt", priority=0, **kwargs)


def test_apply_playing_sets_state_and_both_timestamps():
    s = src()
    agg.apply_state(s, PlaybackState.PLAYING, NOW)
    assert s.state == PlaybackState.PLAYING
    assert s.last_event_at == NOW
    assert s.last_playing_at == NOW


def test_apply_paused_sets_state_and_last_playing_at():
    s = src()
    agg.apply_state(s, PlaybackState.PAUSED, NOW)
    assert s.state == PlaybackState.PAUSED
    assert s.last_playing_at == NOW


def test_apply_stopped_preserves_last_playing_at():
    played_at = NOW - timedelta(seconds=5)
    s = src(last_playing_at=played_at)
    agg.apply_state(s, PlaybackState.STOPPED, NOW)
    assert s.state == PlaybackState.STOPPED
    assert s.last_playing_at == played_at
