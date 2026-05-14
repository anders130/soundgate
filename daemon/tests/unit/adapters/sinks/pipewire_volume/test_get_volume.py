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
async def test_get_volume_parses_wpctl_output(tmp_path) -> None:
    adapter = make_adapter(FakeWpctl("Volume: 0.70\n"), tmp_path)
    assert await adapter.get_volume() == 0.70


@pytest.mark.asyncio
async def test_get_volume_parses_muted_output(tmp_path) -> None:
    adapter = make_adapter(FakeWpctl("Volume: 0.45 [MUTED]\n"), tmp_path)
    assert await adapter.get_volume() == 0.45


@pytest.mark.asyncio
async def test_get_volume_returns_default_on_failure(tmp_path) -> None:
    adapter = make_adapter(FakeWpctl(None), tmp_path)
    assert await adapter.get_volume() == 1.0
