import pytest

from soundgate.adapters.sources.bluetooth import BluetoothAdapter
from soundgate.domain.events import PlaybackState

from .conftest import FakeEventPort


@pytest.mark.asyncio
async def test_stores_media_player_path(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_player_added("/org/bluez/player0", {})
    assert adapter._media_player_path == "/org/bluez/player0"


@pytest.mark.asyncio
async def test_emits_state_from_status(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_player_added("/org/bluez/player0", {"Status": "playing"})
    assert port.events[-1].state == PlaybackState.PLAYING


@pytest.mark.asyncio
async def test_missing_status_defaults_to_stopped(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_player_added("/org/bluez/player0", {})
    assert port.events[-1].state == PlaybackState.STOPPED


@pytest.mark.asyncio
async def test_emits_metadata_from_track(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_player_added(
        "/org/bluez/player0", {"Track": {"Title": "Song", "Artist": "Artist"}}
    )
    assert port.events[-1].metadata is not None
    assert port.events[-1].metadata.title == "Song"


@pytest.mark.asyncio
async def test_emits_normalized_volume(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_player_added("/org/bluez/player0", {"Volume": 127})
    assert port.events[-1].volume == pytest.approx(1.0)


@pytest.mark.asyncio
async def test_missing_volume_is_none(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_player_added("/org/bluez/player0", {})
    assert port.events[-1].volume is None
