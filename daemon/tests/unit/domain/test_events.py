from soundgate.domain.events import Metadata, PlaybackState


def test_playback_state_values():
    assert PlaybackState.PLAYING == "playing"
    assert PlaybackState.PAUSED == "paused"
    assert PlaybackState.STOPPED == "stopped"


def test_metadata_equality_by_value():
    assert Metadata(title="Song") == Metadata(title="Song")
    assert Metadata(title="Song") != Metadata(title="Other")
