from soundgate.domain.events import Metadata, PlaybackState
from soundgate.domain.source import Source


def test_source_defaults_to_stopped():
    s = Source(name="bluetooth", priority=0)
    assert s.state == PlaybackState.STOPPED


def test_source_defaults_metadata_empty():
    s = Source(name="bluetooth", priority=0)
    assert s.metadata == Metadata()


def test_source_no_timestamps_initially():
    s = Source(name="bluetooth", priority=0)
    assert s.last_playing_at is None
    assert s.last_event_at is None


def test_source_state_is_mutable():
    s = Source(name="bluetooth", priority=0)
    s.state = PlaybackState.PLAYING
    assert s.state == PlaybackState.PLAYING
