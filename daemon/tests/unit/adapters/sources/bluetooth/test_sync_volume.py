from __future__ import annotations

import pytest

from soundgate.adapters.sources.bluetooth import BluetoothAdapter

from .conftest import FakeBus, FakeEventPort


@pytest.mark.asyncio
async def test_sync_volume_sends_avrcp_set(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    bus = FakeBus()
    adapter._bus = bus
    adapter._transport_paths = {"/org/bluez/hci0/dev/fd0"}
    await adapter.sync_volume(0.5)
    assert len(bus.calls) == 1
    msg = bus.calls[0]
    assert msg.member == "Set"
    assert msg.body[1] == "Volume"
    assert msg.body[2].value == round(0.5 * 127)


@pytest.mark.asyncio
async def test_sync_volume_clamped_to_127(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    bus = FakeBus()
    adapter._bus = bus
    adapter._transport_paths = {"/transport/0"}
    await adapter.sync_volume(1.0)
    assert bus.calls[0].body[2].value == 127


@pytest.mark.asyncio
async def test_sync_volume_zero(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    bus = FakeBus()
    adapter._bus = bus
    adapter._transport_paths = {"/transport/0"}
    await adapter.sync_volume(0.0)
    assert bus.calls[0].body[2].value == 0


@pytest.mark.asyncio
async def test_sync_volume_no_bus_is_noop(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    adapter._transport_paths = {"/transport/0"}
    await adapter.sync_volume(0.5)  # must not raise


@pytest.mark.asyncio
async def test_sync_volume_no_transport_paths_is_noop(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    bus = FakeBus()
    adapter._bus = bus
    await adapter.sync_volume(0.5)
    assert bus.calls == []


@pytest.mark.asyncio
async def test_sync_volume_multiple_transports(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    bus = FakeBus()
    adapter._bus = bus
    adapter._transport_paths = {"/transport/0", "/transport/1"}
    await adapter.sync_volume(0.5)
    assert len(bus.calls) == 2
