import pytest

from soundgate.domain.events import PlaybackState

from .conftest import FakeEventPort, enc, make_adapter


async def test_started_maps_to_playing(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="started", track_id="spotify:track:abc"))
    assert port.events[-1].state == PlaybackState.PLAYING


async def test_playing_maps_to_playing(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="playing", position_ms="5000"))
    assert port.events[-1].state == PlaybackState.PLAYING


async def test_paused_maps_to_paused(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="paused", position_ms="1000"))
    assert port.events[-1].state == PlaybackState.PAUSED


async def test_stopped_maps_to_stopped(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="stopped"))
    assert port.events[-1].state == PlaybackState.STOPPED


async def test_unavailable_maps_to_stopped(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="unavailable"))
    assert port.events[-1].state == PlaybackState.STOPPED


async def test_source_name_is_spotify(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="started"))
    assert port.events[-1].source == "spotify"
