import pytest

from soundgate.adapters.sources.bluetooth import BluetoothAdapter
from soundgate.domain.events import PlaybackState

from .conftest import FakeEventPort


@pytest.mark.asyncio
async def test_connected_true_emits_playing(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._device_props_changed("/dev/bt0", {"Connected": True})
    assert port.events[-1].state == PlaybackState.PLAYING


@pytest.mark.asyncio
async def test_connected_false_emits_stopped(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._device_connected("/dev/bt0")
    await adapter._device_props_changed("/dev/bt0", {"Connected": False})
    assert port.events[-1].state == PlaybackState.STOPPED


@pytest.mark.asyncio
async def test_connected_false_one_of_two_no_stopped(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._device_connected("/dev/bt0")
    await adapter._device_connected("/dev/bt1")
    await adapter._device_props_changed("/dev/bt0", {"Connected": False})
    assert port.events[-1].state != PlaybackState.STOPPED


@pytest.mark.asyncio
async def test_no_connected_key_emits_no_event(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._device_props_changed("/dev/bt0", {"RSSI": -60})
    assert port.events == []
