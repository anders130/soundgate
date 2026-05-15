from __future__ import annotations

import asyncio
import json
import logging
import os
import pathlib
import socket

from soundgate.application.ports.inbound import PlayerEventPort
from soundgate.domain.events import Metadata, PlaybackState, PlayerEvent

_log = logging.getLogger(__name__)

_SOURCE = "spotify"

_STATE_MAP: dict[str, PlaybackState | None] = {
    "started": PlaybackState.PLAYING,
    "playing": PlaybackState.PLAYING,
    "paused": PlaybackState.PAUSED,
    "stopped": PlaybackState.STOPPED,
    "changed": None,
    "track_changed": None,
    "volume_changed": None,
    "preloading": None,
    "loading": None,
    "unavailable": PlaybackState.STOPPED,
    "session_connected": None,
    "session_disconnected": None,
    "session_client_changed": None,
    "auto_play_changed": None,
    "filter_explicit_content_changed": None,
    "shuffle_changed": None,
    "repeat_changed": None,
    "play_request_id_changed": None,
}

_TRACK_EVENTS = {"changed", "track_changed"}


def _parse_track(msg: dict) -> Metadata:
    duration_ms = msg.get("duration_ms", "")
    return Metadata(
        title=msg.get("name") or None,
        artist=msg.get("artists") or None,
        album=msg.get("album") or None,
        art_url=msg.get("cover_url") or None,
        duration_us=int(duration_ms) * 1000 if duration_ms else None,
        track_id=msg.get("track_id") or None,
    )


def _parse_volume(msg: dict) -> float | None:
    raw = msg.get("volume", "")
    return int(raw) / 65535.0 if raw else None


def _parse_position(msg: dict) -> int | None:
    pos = msg.get("position_ms", "")
    return int(pos) * 1000 if pos else None


_SESSION_RESET_EVENTS = {"session_disconnected", "session_client_changed"}


class LibrespotAdapter:
    def __init__(self, socket_path: str, event_port: PlayerEventPort) -> None:
        self._socket_path = socket_path
        self._port = event_port
        self._heartbeat_task: asyncio.Task | None = None
        self._session_active = False

    @classmethod
    def from_env(cls, event_port: PlayerEventPort) -> LibrespotAdapter:
        path = os.environ.get(
            "SOUNDGATE_LIBRESPOT_SOCKET", "/run/soundgate/librespot.sock"
        )
        return cls(path, event_port)

    async def run(self) -> None:
        p = pathlib.Path(self._socket_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.unlink(missing_ok=True)

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        sock.setblocking(False)
        sock.bind(self._socket_path)
        os.chmod(self._socket_path, 0o666)

        _log.info("librespot adapter listening on %s", self._socket_path)
        loop = asyncio.get_running_loop()
        try:
            while True:
                data = await loop.sock_recv(sock, 4096)
                await self._handle(data)
        finally:
            sock.close()
            p.unlink(missing_ok=True)

    async def _handle(self, data: bytes) -> None:
        try:
            msg: dict = json.loads(data.decode())
        except Exception:
            return

        ev = msg.get("event", "")
        if ev not in _STATE_MAP:
            return

        if ev == "playing":
            self._session_active = True
        elif ev in _SESSION_RESET_EVENTS:
            self._session_active = False

        state = _STATE_MAP[ev]
        metadata = _parse_track(msg) if ev in _TRACK_EVENTS else None
        volume = (
            _parse_volume(msg)
            if ev == "volume_changed" and self._session_active
            else None
        )
        position_us = _parse_position(msg) if ev in ("playing", "paused") else None

        if state is None and metadata is None and volume is None:
            return

        if state == PlaybackState.PLAYING:
            self._start_heartbeat()
        elif state in (PlaybackState.STOPPED, PlaybackState.PAUSED):
            self._stop_heartbeat()

        await self._port.handle_event(
            PlayerEvent(
                source=_SOURCE,
                state=state,
                metadata=metadata,
                volume=volume,
                position_us=position_us,
            )
        )

    def _start_heartbeat(self) -> None:
        if self._heartbeat_task and not self._heartbeat_task.done():
            return
        self._heartbeat_task = asyncio.get_running_loop().create_task(self._heartbeat())

    def _stop_heartbeat(self) -> None:
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            self._heartbeat_task = None

    async def _heartbeat(self) -> None:
        while True:
            await asyncio.sleep(7)
            await self._port.handle_event(
                PlayerEvent(source=_SOURCE, state=PlaybackState.PLAYING)
            )
