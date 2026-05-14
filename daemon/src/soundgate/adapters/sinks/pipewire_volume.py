import asyncio
import os
from collections.abc import Awaitable, Callable
from pathlib import Path

_WPCTL_TIMEOUT = 2.0

WpctlFn = Callable[..., Awaitable[str | None]]


async def _wpctl_subprocess(*args: str) -> str | None:
    try:
        proc = await asyncio.create_subprocess_exec(
            "wpctl",
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=_WPCTL_TIMEOUT)
        return stdout.decode()
    except Exception:
        return None


class PipewireVolumeAdapter:
    def __init__(
        self,
        sink: str = "@DEFAULT_SINK@",
        volume_file: Path = Path("/var/cache/soundgate/volume"),
        wpctl_fn: WpctlFn = _wpctl_subprocess,
    ) -> None:
        self._sink = sink
        self._volume_file = volume_file
        self._wpctl = wpctl_fn

    @classmethod
    def from_env(cls) -> "PipewireVolumeAdapter":
        return cls(
            sink=os.environ.get("SOUNDGATE_PIPEWIRE_SINK", "@DEFAULT_SINK@"),
            volume_file=Path(
                os.environ.get("SOUNDGATE_CACHE_DIR", "/var/cache/soundgate")
            )
            / "volume",
        )

    async def set_volume(self, level: float) -> None:
        clamped = max(0.0, min(1.0, level))
        await self._wpctl("set-volume", self._sink, f"{clamped:.3f}")
        try:
            self._volume_file.parent.mkdir(parents=True, exist_ok=True)
            self._volume_file.write_text(str(clamped))
        except OSError:
            pass

    async def get_volume(self) -> float:
        out = await self._wpctl("get-volume", self._sink)
        if not out:
            return 1.0
        parts = out.split()
        if len(parts) < 2:
            return 1.0
        try:
            return float(parts[1])
        except ValueError:
            return 1.0

    async def restore_saved(self) -> float | None:
        try:
            saved = float(self._volume_file.read_text().strip())
            clamped = max(0.0, min(1.0, saved))
            await self.set_volume(clamped)
            return clamped
        except (OSError, ValueError):
            return None
