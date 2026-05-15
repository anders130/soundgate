import pytest

from soundgate.adapters.sinks.pipewire_volume import PipewireVolumeAdapter

from .conftest import FakeWpctl


def make_adapter(wpctl: FakeWpctl, tmp_path) -> PipewireVolumeAdapter:
    return PipewireVolumeAdapter(
        sink="@DEFAULT_SINK@",
        volume_file=tmp_path / "volume",
        wpctl_fn=wpctl,
    )


@pytest.mark.asyncio
async def test_set_volume_calls_wpctl(wpctl: FakeWpctl, tmp_path) -> None:
    adapter = make_adapter(wpctl, tmp_path)
    await adapter.set_volume(0.7)
    assert wpctl.calls == [("set-volume", "@DEFAULT_SINK@", "0.700")]


@pytest.mark.asyncio
async def test_set_volume_persists_to_file(wpctl: FakeWpctl, tmp_path) -> None:
    adapter = make_adapter(wpctl, tmp_path)
    await adapter.set_volume(0.7)
    assert (tmp_path / "volume").read_text() == "0.7"


@pytest.mark.asyncio
async def test_set_volume_clamps_below_zero(wpctl: FakeWpctl, tmp_path) -> None:
    adapter = make_adapter(wpctl, tmp_path)
    await adapter.set_volume(-0.5)
    assert wpctl.calls[0][2] == "0.000"


@pytest.mark.asyncio
async def test_set_volume_clamps_above_one(wpctl: FakeWpctl, tmp_path) -> None:
    adapter = make_adapter(wpctl, tmp_path)
    await adapter.set_volume(1.5)
    assert wpctl.calls[0][2] == "1.000"


@pytest.mark.asyncio
async def test_set_volume_passthrough_skips_wpctl(wpctl: FakeWpctl, tmp_path) -> None:
    adapter = PipewireVolumeAdapter(
        sink="@DEFAULT_SINK@",
        volume_file=tmp_path / "volume",
        wpctl_fn=wpctl,
        control_pipewire=False,
    )
    await adapter.set_volume(0.7)
    assert wpctl.calls == []
    assert (tmp_path / "volume").read_text() == "0.7"
