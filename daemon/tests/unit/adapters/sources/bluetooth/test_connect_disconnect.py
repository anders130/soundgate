import pytest
from soundgate.adapters.sources.bluetooth import BluetoothAdapter
from soundgate.domain.events import PlaybackState

from .conftest import FakeEventPort


@pytest.mark.asyncio
async def test_device_connected_emits_playing(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._device_connected("/dev/bt0", {})
    assert port.events[-1].state == PlaybackState.PLAYING


@pytest.mark.asyncio
async def test_device_disconnected_emits_stopped(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._device_connected("/dev/bt0", {})
    await adapter._device_disconnected("/dev/bt0")
    assert port.events[-1].state == PlaybackState.STOPPED


@pytest.mark.asyncio
async def test_one_of_two_disconnects_does_not_emit_stopped(
    port: FakeEventPort,
) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._device_connected("/dev/bt0", {})
    await adapter._device_connected("/dev/bt1", {})
    await adapter._device_disconnected("/dev/bt0")
    assert port.events[-1].state != PlaybackState.STOPPED


@pytest.mark.asyncio
async def test_all_devices_disconnected_emits_stopped(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._device_connected("/dev/bt0", {})
    await adapter._device_connected("/dev/bt1", {})
    await adapter._device_disconnected("/dev/bt0")
    await adapter._device_disconnected("/dev/bt1")
    assert port.events[-1].state == PlaybackState.STOPPED
