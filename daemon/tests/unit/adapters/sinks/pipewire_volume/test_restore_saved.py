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
async def test_restore_saved_applies_persisted_volume(
    wpctl: FakeWpctl, tmp_path
) -> None:
    (tmp_path / "volume").write_text("0.65")
    adapter = make_adapter(wpctl, tmp_path)
    result = await adapter.restore_saved()
    assert result == 0.65
    assert wpctl.calls == [("set-volume", "@DEFAULT_SINK@", "0.650")]


@pytest.mark.asyncio
async def test_restore_saved_returns_none_when_no_file(
    wpctl: FakeWpctl, tmp_path
) -> None:
    adapter = make_adapter(wpctl, tmp_path)
    assert await adapter.restore_saved() is None
    assert wpctl.calls == []


@pytest.mark.asyncio
async def test_restore_saved_clamps_persisted_value(wpctl: FakeWpctl, tmp_path) -> None:
    (tmp_path / "volume").write_text("1.5")
    adapter = make_adapter(wpctl, tmp_path)
    result = await adapter.restore_saved()
    assert result == 1.0
