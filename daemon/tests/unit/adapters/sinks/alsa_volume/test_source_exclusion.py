from soundgate.adapters.sinks.alsa_volume import AlsaVolumeAdapter

from .conftest import FakeAmixer


def make_adapter(amixer: FakeAmixer) -> AlsaVolumeAdapter:
    return AlsaVolumeAdapter(control="Master", device="default", amixer_fn=amixer)


async def test_spotify_source_suppressed(amixer: FakeAmixer) -> None:
    adapter = make_adapter(amixer)
    await adapter.sync_volume(0.5, source="spotify")
    assert amixer.calls == []


async def test_bluetooth_source_allowed(amixer: FakeAmixer) -> None:
    adapter = make_adapter(amixer)
    await adapter.sync_volume(0.5, source="bluetooth")
    assert len(amixer.calls) == 1


async def test_none_source_allowed(amixer: FakeAmixer) -> None:
    adapter = make_adapter(amixer)
    await adapter.sync_volume(0.5, source=None)
    assert len(amixer.calls) == 1


async def test_unknown_source_allowed(amixer: FakeAmixer) -> None:
    adapter = make_adapter(amixer)
    await adapter.sync_volume(0.5, source="radio")
    assert len(amixer.calls) == 1


async def test_suppression_does_not_update_last_percent(amixer: FakeAmixer) -> None:
    adapter = make_adapter(amixer)
    await adapter.sync_volume(0.5, source="spotify")  # suppressed
    await adapter.sync_volume(0.5, source=None)  # same value, but first real call
    assert len(amixer.calls) == 1
