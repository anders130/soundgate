import pytest

from soundgate.adapters.sources.bluetooth import BluetoothAdapter

from .conftest import FakeBus, FakeEventPort


@pytest.mark.asyncio
async def test_transport_added_does_not_emit_volume(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_transport_added("/transport/0", {"Volume": 80})
    assert all(e.volume is None for e in port.events)


@pytest.mark.asyncio
async def test_transport_added_emits_no_events_at_all(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_transport_added("/transport/0", {"Volume": 80})
    assert port.events == []


@pytest.mark.asyncio
async def test_transport_added_registers_path(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_transport_added("/transport/0", {})
    assert "/transport/0" in adapter._transport_paths


@pytest.mark.asyncio
async def test_transport_added_syncs_current_volume(
    port: FakeEventPort, bus: FakeBus
) -> None:
    adapter = BluetoothAdapter(port, volume_provider=lambda: 0.5)
    adapter._bus = bus
    await adapter._media_transport_added("/transport/0", {"Volume": 80})
    assert len(bus.calls) == 1
    msg = bus.calls[0]
    assert msg.member == "Set"
    assert msg.body[1] == "Volume"
    assert msg.body[2].value == round(0.5 * 127)


@pytest.mark.asyncio
async def test_transport_added_no_sync_without_provider(
    port: FakeEventPort, bus: FakeBus
) -> None:
    adapter = BluetoothAdapter(port)
    adapter._bus = bus
    await adapter._media_transport_added("/transport/0", {"Volume": 80})
    assert bus.calls == []


@pytest.mark.asyncio
async def test_transport_added_no_sync_without_bus(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port, volume_provider=lambda: 0.5)
    await adapter._media_transport_added("/transport/0", {"Volume": 80})
    # must not raise, no sync attempted


@pytest.mark.asyncio
async def test_initial_phone_volume_echo_suppressed(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    adapter._initial_transport_raw = 30
    await adapter._media_transport_props_changed({"Volume": 30})
    assert port.events == []


@pytest.mark.asyncio
async def test_initial_transport_raw_cleared_after_add(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_transport_added("/transport/0", {"Volume": 30})
    assert adapter._initial_transport_raw is None


@pytest.mark.asyncio
async def test_different_volume_after_add_not_suppressed(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    adapter._initial_transport_raw = 30
    await adapter._media_transport_props_changed({"Volume": 80})
    assert port.events[-1].volume == pytest.approx(80 / 127.0)
