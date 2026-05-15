import pytest

from soundgate.adapters.sources.bluetooth import BluetoothAdapter

from .conftest import FakeEventPort


@pytest.mark.asyncio
async def test_transport_volume_max(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_transport_props_changed({"Volume": 127})
    assert port.events[-1].volume == pytest.approx(1.0)


@pytest.mark.asyncio
async def test_transport_volume_zero(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_transport_props_changed({"Volume": 0})
    assert port.events[-1].volume == pytest.approx(0.0)


@pytest.mark.asyncio
async def test_transport_no_volume_emits_no_event(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_transport_props_changed({})
    assert port.events == []


@pytest.mark.asyncio
async def test_echo_from_sync_volume_suppressed(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    adapter._last_synced_raw = 64
    await adapter._media_transport_props_changed({"Volume": 64})
    assert port.events == []


@pytest.mark.asyncio
async def test_different_value_after_sync_not_suppressed(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    adapter._last_synced_raw = 64
    await adapter._media_transport_props_changed({"Volume": 80})
    assert port.events[-1].volume == pytest.approx(80 / 127.0)
