from datetime import datetime, timedelta

from soundgate.domain.aggregator import AggregatorService
from soundgate.domain.events import PlaybackState
from soundgate.domain.source import Source

NOW = datetime(2024, 1, 1, 12, 0, 0)

agg = AggregatorService(inactivity_timeout=10)


def test_touch_resets_inactivity_timer():
    s = Source(
        name="bt",
        priority=0,
        state=PlaybackState.PLAYING,
        last_event_at=NOW - timedelta(seconds=9),
    )
    agg.touch(s, NOW)
    assert s.last_event_at == NOW
