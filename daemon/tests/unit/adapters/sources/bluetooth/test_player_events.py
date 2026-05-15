import pytest

from soundgate.adapters.sources.bluetooth import BluetoothAdapter
from soundgate.domain.events import PlaybackState

from .conftest import FakeEventPort


class FakeVariant:
    def __init__(self, value: object) -> None:
        self.value = value


@pytest.mark.asyncio
async def test_variant_status_playing_emits_playing(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_player_props_changed({"Status": FakeVariant("playing")})
    assert port.events[-1].state == PlaybackState.PLAYING


@pytest.mark.asyncio
async def test_variant_status_paused_emits_paused(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_player_props_changed({"Status": FakeVariant("paused")})
    assert port.events[-1].state == PlaybackState.PAUSED


@pytest.mark.asyncio
async def test_variant_track_change_emits_metadata(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_player_props_changed(
        {"Track": FakeVariant({"Title": "Song", "Artist": "Artist"})}
    )
    assert port.events[-1].metadata is not None
    assert port.events[-1].metadata.title == "Song"


@pytest.mark.asyncio
async def test_variant_volume_emits_normalized_volume(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_player_props_changed({"Volume": FakeVariant(127)})
    assert port.events[-1].volume == pytest.approx(1.0)


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
    assert port.events[-1].volume == pytest.approx(1.0)  # active change, not init


@pytest.mark.asyncio
async def test_no_changed_fields_emits_no_event(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_player_props_changed({})
    assert port.events == []


@pytest.mark.asyncio
async def test_media_player_volume_echo_suppressed(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    adapter._last_synced_raw = 64
    await adapter._media_player_props_changed({"Volume": 64})
    assert all(e.volume is None for e in port.events)


@pytest.mark.asyncio
async def test_media_player_volume_different_not_suppressed(
    port: FakeEventPort,
) -> None:
    adapter = BluetoothAdapter(port)
    adapter._last_synced_raw = 64
    await adapter._media_player_props_changed({"Volume": 80})
    assert port.events[-1].volume == pytest.approx(80 / 127.0)
