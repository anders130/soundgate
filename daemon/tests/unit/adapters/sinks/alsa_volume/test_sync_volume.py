import pytest

from soundgate.adapters.sinks.alsa_volume import AlsaVolumeAdapter

from .conftest import FakeAmixer


def make_adapter(amixer: FakeAmixer) -> AlsaVolumeAdapter:
    return AlsaVolumeAdapter(control="Master", device="default", amixer_fn=amixer)


async def test_sync_volume_calls_amixer(amixer: FakeAmixer) -> None:
    adapter = make_adapter(amixer)
    await adapter.sync_volume(0.5)
    assert amixer.calls == [("default", "Master", 50)]


async def test_sync_volume_converts_to_percent(amixer: FakeAmixer) -> None:
    adapter = make_adapter(amixer)
    await adapter.sync_volume(0.75)
    assert amixer.calls[-1][2] == 75


async def test_sync_volume_rounds_percent(amixer: FakeAmixer) -> None:
    adapter = make_adapter(amixer)
    await adapter.sync_volume(0.999)
    assert amixer.calls[-1][2] == 100


async def test_sync_volume_clamps_below_zero(amixer: FakeAmixer) -> None:
    adapter = make_adapter(amixer)
    await adapter.sync_volume(-0.5)
    assert amixer.calls[-1][2] == 0


async def test_sync_volume_clamps_above_one(amixer: FakeAmixer) -> None:
    adapter = make_adapter(amixer)
    await adapter.sync_volume(1.5)
    assert amixer.calls[-1][2] == 100


async def test_repeated_same_value_suppressed(amixer: FakeAmixer) -> None:
    adapter = make_adapter(amixer)
    await adapter.sync_volume(0.5)
    await adapter.sync_volume(0.5)
    assert len(amixer.calls) == 1


async def test_near_same_value_suppressed(amixer: FakeAmixer) -> None:
    adapter = make_adapter(amixer)
    await adapter.sync_volume(0.501)
    await adapter.sync_volume(0.504)  # both round to 50%
    assert len(amixer.calls) == 1


async def test_different_value_fires(amixer: FakeAmixer) -> None:
    adapter = make_adapter(amixer)
    await adapter.sync_volume(0.5)
    await adapter.sync_volume(0.7)
    assert len(amixer.calls) == 2
    assert amixer.calls[1][2] == 70


async def test_passes_device_and_control(amixer: FakeAmixer) -> None:
    adapter = AlsaVolumeAdapter(control="PCM", device="hw:0", amixer_fn=amixer)
    await adapter.sync_volume(0.3)
    assert amixer.calls[0] == ("hw:0", "PCM", 30)
