from soundgate.adapters.sources.bluetooth import _parse_track
from soundgate.domain.events import Metadata


def test_empty_track_returns_empty_metadata() -> None:
    assert _parse_track({}) == Metadata()


def test_parse_title_artist_album() -> None:
    m = _parse_track({"Title": "Song", "Artist": "Artist", "Album": "Album"})
    assert m.title == "Song"
    assert m.artist == "Artist"
    assert m.album == "Album"


def test_duration_converted_from_ms_to_us() -> None:
    m = _parse_track({"Duration": 90_000})
    assert m.duration_us == 90_000_000


def test_missing_duration_is_none() -> None:
    assert _parse_track({}).duration_us is None


def test_empty_string_fields_become_none() -> None:
    m = _parse_track({"Title": "", "Artist": ""})
    assert m.title is None
    assert m.artist is None
