from soundgate.domain.events import PlaybackState

from .conftest import FakeEventPort, enc, make_adapter


async def test_start_maps_to_playing(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="start"))
    assert port.events[-1].state == PlaybackState.PLAYING


async def test_play_maps_to_playing(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="play"))
    assert port.events[-1].state == PlaybackState.PLAYING


async def test_playing_maps_to_playing(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="playing", position_ms="5000"))
    assert port.events[-1].state == PlaybackState.PLAYING


async def test_pause_maps_to_paused(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="pause", position_ms="1000"))
    assert port.events[-1].state == PlaybackState.PAUSED


async def test_paused_maps_to_paused(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="paused", position_ms="1000"))
    assert port.events[-1].state == PlaybackState.PAUSED


async def test_stop_maps_to_stopped(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="stop"))
    assert port.events[-1].state == PlaybackState.STOPPED


async def test_stopped_maps_to_stopped(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="stopped"))
    assert port.events[-1].state == PlaybackState.STOPPED


async def test_source_name_is_spotify(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="start"))
    assert port.events[-1].source == "spotify"
