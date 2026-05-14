from datetime import datetime, timedelta

from .events import PlaybackState
from .source import Source


class AggregatorService:
    """Active-source selection. No I/O, no async.

    Rules (applied in order):
    1. PLAYING eligible if last_event_at within inactivity_timeout.
    2. PAUSED always eligible; adapter emits STOPPED on disconnect.
    3. Lower priority index wins (0 = most preferred).
    4. Tiebreak: most recently played wins.
    """

    def __init__(self, inactivity_timeout: int = 10) -> None:
        self._inactivity = timedelta(seconds=inactivity_timeout)

    def active_source(self, sources: dict[str, Source], now: datetime) -> Source | None:
        candidates = [s for s in sources.values() if self._is_candidate(s, now)]
        if not candidates:
            return None
        return min(
            candidates,
            key=lambda s: (
                s.priority,
                -(s.last_playing_at.timestamp() if s.last_playing_at else 0.0),
            ),
        )

    def _is_candidate(self, source: Source, now: datetime) -> bool:
        if source.state == PlaybackState.PLAYING:
            return (
                source.last_event_at is not None
                and (now - source.last_event_at) < self._inactivity
            )
        return source.state == PlaybackState.PAUSED

    def apply_state(self, source: Source, state: PlaybackState, now: datetime) -> None:
        source.state = state
        source.last_event_at = now
        if state in (PlaybackState.PLAYING, PlaybackState.PAUSED):
            source.last_playing_at = now

    def touch(self, source: Source, now: datetime) -> None:
        source.last_event_at = now
        source.last_playing_at = now
