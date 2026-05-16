import pytest

from soundgate.adapters.sinks.alsa_volume import AlsaVolumeAdapter


async def test_from_env_returns_none_if_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SOUNDGATE_ALSA_VOLUME_SYNC_CONTROL", raising=False)
    assert AlsaVolumeAdapter.from_env() is None


async def test_from_env_returns_adapter_if_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOUNDGATE_ALSA_VOLUME_SYNC_CONTROL", "Master")
    adapter = AlsaVolumeAdapter.from_env()
    assert adapter is not None


async def test_from_env_reads_control(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOUNDGATE_ALSA_VOLUME_SYNC_CONTROL", "PCM")
    adapter = AlsaVolumeAdapter.from_env()
    assert adapter is not None
    assert adapter._control == "PCM"


async def test_from_env_default_device(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOUNDGATE_ALSA_VOLUME_SYNC_CONTROL", "Master")
    monkeypatch.delenv("SOUNDGATE_ALSA_VOLUME_SYNC_DEVICE", raising=False)
    adapter = AlsaVolumeAdapter.from_env()
    assert adapter is not None
    assert adapter._device == "default"


async def test_from_env_reads_device(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOUNDGATE_ALSA_VOLUME_SYNC_CONTROL", "Master")
    monkeypatch.setenv("SOUNDGATE_ALSA_VOLUME_SYNC_DEVICE", "hw:1")
    adapter = AlsaVolumeAdapter.from_env()
    assert adapter is not None
    assert adapter._device == "hw:1"
