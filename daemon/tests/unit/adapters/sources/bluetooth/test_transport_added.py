import asyncio

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
async def test_phone_volume_suppressed_immediately_after_add(
    port: FakeEventPort,
) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_transport_added("/transport/0", {"Volume": 80})
    await adapter._media_transport_props_changed({"Volume": 80})
    assert port.events == []


@pytest.mark.asyncio
async def test_phone_volume_suppressed_shortly_after_add(
    port: FakeEventPort,
) -> None:
    adapter = BluetoothAdapter(port)
    await adapter._media_transport_added("/transport/0", {"Volume": 80})
    # volume event arriving shortly after add (phone revert) must be suppressed
    await adapter._media_transport_props_changed({"Volume": 80})
    assert port.events == []


@pytest.mark.asyncio
async def test_phone_volume_accepted_after_suppress_window(
    port: FakeEventPort,
) -> None:
    adapter = BluetoothAdapter(port)
    adapter._volume_suppress_deadline = 0.0  # expired
    await adapter._media_transport_props_changed({"Volume": 80})
    assert port.events[-1].volume == pytest.approx(80 / 127.0)


@pytest.mark.asyncio
async def test_different_volume_after_suppress_window_accepted(
    port: FakeEventPort,
) -> None:
    adapter = BluetoothAdapter(port)
    adapter._volume_suppress_deadline = 0.0  # expired
    await adapter._media_transport_props_changed({"Volume": 50})
    assert port.events[-1].volume == pytest.approx(50 / 127.0)
