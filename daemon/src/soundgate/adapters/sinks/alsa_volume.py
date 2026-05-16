from __future__ import annotations

import asyncio
import os
from collections.abc import Callable, Coroutine
from typing import Any

_AmixerFn = Callable[[str, str, int], Coroutine[Any, Any, None]]


async def _amixer_subprocess(device: str, control: str, percent: int) -> None:
    try:
        proc = await asyncio.create_subprocess_exec(
            "amixer",
            "-D",
            device,
            "sset",
            control,
            f"{percent}%",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await asyncio.wait_for(proc.wait(), timeout=2.0)
    except Exception:
        pass


_DEFAULT_EXCLUDE: frozenset[str] = frozenset({"spotify"})


class AlsaVolumeAdapter:
    def __init__(
        self,
        control: str,
        device: str = "default",
        amixer_fn: _AmixerFn = _amixer_subprocess,
        exclude_sources: frozenset[str] = _DEFAULT_EXCLUDE,
    ) -> None:
        self._control = control
        self._device = device
        self._amixer = amixer_fn
        self._exclude_sources = exclude_sources
        self._last_percent: int | None = None

    @classmethod
    def from_env(cls) -> AlsaVolumeAdapter | None:
        control = os.environ.get("SOUNDGATE_ALSA_VOLUME_SYNC_CONTROL")
        if not control:
            return None
        device = os.environ.get("SOUNDGATE_ALSA_VOLUME_SYNC_DEVICE", "default")
        return cls(control=control, device=device)

    async def sync_volume(self, level: float, source: str | None = None) -> None:
        if source in self._exclude_sources:
            return
        percent = round(max(0.0, min(1.0, level)) * 100)
        if percent == self._last_percent:
            return
        self._last_percent = percent
        await self._amixer(self._device, self._control, percent)
