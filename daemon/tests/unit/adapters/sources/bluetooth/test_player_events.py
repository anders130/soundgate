import pytest

from soundgate.adapters.sources.bluetooth import BluetoothAdapter
from soundgate.domain.events import PlaybackState

from .conftest import FakeEventPort


@pytest.mark.asyncio
async def test_status_playing_emits_playing(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_player_props_changed({"Status": "playing"})
    assert port.events[-1].state == PlaybackState.PLAYING


@pytest.mark.asyncio
async def test_status_paused_emits_paused(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_player_props_changed({"Status": "paused"})
    assert port.events[-1].state == PlaybackState.PAUSED


@pytest.mark.asyncio
async def test_status_stopped_emits_stopped(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_player_props_changed({"Status": "stopped"})
    assert port.events[-1].state == PlaybackState.STOPPED


@pytest.mark.asyncio
async def test_forward_seek_emits_playing(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_player_props_changed({"Status": "forward-seek"})
    assert port.events[-1].state == PlaybackState.PLAYING


@pytest.mark.asyncio
async def test_track_change_emits_metadata(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_player_props_changed(
        {"Track": {"Title": "Song", "Artist": "Artist"}}
    )
    assert port.events[-1].metadata is not None
    assert port.events[-1].metadata.title == "Song"


@pytest.mark.asyncio
async def test_volume_change_emits_normalized_volume(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_player_props_changed({"Volume": 127})
    assert port.events[-1].volume == pytest.approx(1.0)


@pytest.mark.asyncio
async def test_no_changed_fields_emits_no_event(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_player_props_changed({})
    assert port.events == []
