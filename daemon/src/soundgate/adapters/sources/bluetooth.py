import asyncio
import logging
from typing import Any, TypeVar, overload

from dbus_fast import BusType
from dbus_fast.aio import MessageBus
from dbus_fast.constants import MessageType
from dbus_fast.message import Message
from soundgate.domain.events import Metadata, PlaybackState, PlayerEvent

_log = logging.getLogger(__name__)

_SOURCE = "bluetooth"
_A2DP_SOURCE_UUID = "0000110a-0000-1000-8000-00805f9b34fb"
_T = TypeVar("_T")

_BT_STATE_MAP: dict[str, PlaybackState] = {
    "playing": PlaybackState.PLAYING,
    "paused": PlaybackState.PAUSED,
    "stopped": PlaybackState.STOPPED,
    "forward-seek": PlaybackState.PLAYING,
    "reverse-seek": PlaybackState.PLAYING,
    "error": PlaybackState.STOPPED,
}


@overload
def _v(val: Any, default: _T) -> _T: ...
@overload
def _v(val: Any) -> Any: ...
def _v(val: Any, default: Any = None) -> Any:
    return val.value if hasattr(val, "value") else (val if val is not None else default)


def _parse_track(track: dict) -> Metadata:
    duration = track.get("Duration")
    return Metadata(
        title=_v(track.get("Title")) or None,
        artist=_v(track.get("Artist")) or None,
        album=_v(track.get("Album")) or None,
        art_url=_v(track.get("ArtUrl")) or None,
        duration_us=int(_v(duration) or 0) * 1000 if duration is not None else None,
        track_id=_v(track.get("TrackId")) or None,
    )


class BluetoothAdapter:
    def __init__(self, event_port) -> None:
        self._port = event_port
        self._bus: MessageBus | None = None
        self._connected: set[str] = set()
        self._media_player_path: str | None = None

    async def run(self) -> None:
        self._bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

        for rule in [
            "type=signal,sender=org.bluez,interface=org.freedesktop.DBus.Properties,member=PropertiesChanged",
            "type=signal,sender=org.bluez,interface=org.freedesktop.DBus.ObjectManager,member=InterfacesAdded",
            "type=signal,sender=org.bluez,interface=org.freedesktop.DBus.ObjectManager,member=InterfacesRemoved",
        ]:
            await self._bus.call(
                Message(
                    destination="org.freedesktop.DBus",
                    path="/org/freedesktop/DBus",
                    interface="org.freedesktop.DBus",
                    member="AddMatch",
                    signature="s",
                    body=[rule],
                )
            )

        self._bus.add_message_handler(self._on_message)
        await self._scan_existing()
        await self._bus.wait_for_disconnect()

    def _on_message(self, msg: Message) -> None:
        if msg.message_type != MessageType.SIGNAL:
            return
        asyncio.get_running_loop().create_task(self._dispatch(msg))

    async def _dispatch(self, msg: Message) -> None:
        try:
            if msg.member == "PropertiesChanged":
                iface = msg.body[0]
                changed = msg.body[1]
                invalidated = msg.body[2] if len(msg.body) > 2 else []
                path = msg.path or ""
                if iface == "org.bluez.Device1":
                    await self._device_props_changed(path, changed)
                elif iface == "org.bluez.MediaPlayer1":
                    await self._media_player_props_changed(changed)
                    if "Volume" in invalidated:
                        await self._fetch_volume(path, "org.bluez.MediaPlayer1")
                elif iface == "org.bluez.MediaTransport1":
                    await self._media_transport_props_changed(changed)
                    if "Volume" in invalidated:
                        await self._fetch_volume(path, "org.bluez.MediaTransport1")
            elif msg.member == "InterfacesAdded":
                path, ifaces = msg.body
                if "org.bluez.Device1" in ifaces:
                    props = ifaces["org.bluez.Device1"]
                    if _v(props.get("Connected")) and self._has_a2dp(props):
                        await self._device_connected(path)
                if "org.bluez.MediaPlayer1" in ifaces:
                    await self._media_player_added(
                        path, ifaces["org.bluez.MediaPlayer1"]
                    )
                if "org.bluez.MediaTransport1" in ifaces:
                    await self._media_transport_props_changed(
                        ifaces["org.bluez.MediaTransport1"]
                    )
            elif msg.member == "InterfacesRemoved":
                path, ifaces = msg.body
                if "org.bluez.Device1" in ifaces:
                    await self._device_disconnected(path)
                if "org.bluez.MediaPlayer1" in ifaces:
                    if self._media_player_path == path:
                        self._media_player_path = None
        except Exception as e:
            _log.debug("BT dispatch error: %s", e)

    async def _scan_existing(self) -> None:
        if not self._bus:
            return
        try:
            reply = await self._bus.call(
                Message(
                    destination="org.bluez",
                    path="/",
                    interface="org.freedesktop.DBus.ObjectManager",
                    member="GetManagedObjects",
                )
            )
            if not reply.body:
                return
            for path, ifaces in reply.body[0].items():
                if "org.bluez.Device1" in ifaces:
                    props = ifaces["org.bluez.Device1"]
                    if _v(props.get("Connected")) and self._has_a2dp(props):
                        await self._device_connected(path)
                if "org.bluez.MediaPlayer1" in ifaces:
                    await self._media_player_added(
                        path, ifaces["org.bluez.MediaPlayer1"]
                    )
                if "org.bluez.MediaTransport1" in ifaces:
                    await self._media_transport_props_changed(
                        ifaces["org.bluez.MediaTransport1"]
                    )
        except Exception as e:
            _log.warning("BT scan failed: %s", e)

    def _has_a2dp(self, props: dict) -> bool:
        uuids: list[Any] = _v(props.get("UUIDs"), [])
        return any(_v(u, "").lower() == _A2DP_SOURCE_UUID for u in uuids)

    async def _device_props_changed(self, path: str, changed: dict) -> None:
        if "Connected" not in changed:
            return
        if _v(changed["Connected"]):
            self._connected.add(path)
            await self._port.handle_event(
                PlayerEvent(source=_SOURCE, state=PlaybackState.PLAYING)
            )
        else:
            self._connected.discard(path)
            if not self._connected:
                await self._port.handle_event(
                    PlayerEvent(source=_SOURCE, state=PlaybackState.STOPPED)
                )

    async def _device_connected(self, path: str) -> None:
        self._connected.add(path)
        await self._port.handle_event(
            PlayerEvent(source=_SOURCE, state=PlaybackState.PLAYING)
        )

    async def _device_disconnected(self, path: str) -> None:
        self._connected.discard(path)
        if not self._connected:
            await self._port.handle_event(
                PlayerEvent(source=_SOURCE, state=PlaybackState.STOPPED)
            )

    async def _media_player_added(self, path: str, props: dict) -> None:
        self._media_player_path = path
        state = _BT_STATE_MAP.get(
            _v(props.get("Status"), "stopped"), PlaybackState.STOPPED
        )
        track: dict = _v(props.get("Track"), {})
        metadata = _parse_track(track) if track else None
        raw_vol: int | None = _v(props.get("Volume"))
        volume = raw_vol / 127.0 if raw_vol is not None else None
        await self._port.handle_event(
            PlayerEvent(source=_SOURCE, state=state, metadata=metadata, volume=volume)
        )

    async def _media_player_props_changed(self, props: dict) -> None:
        if "Status" in props:
            state = _BT_STATE_MAP.get(props["Status"])
            if state is not None:
                await self._port.handle_event(PlayerEvent(source=_SOURCE, state=state))
        if "Track" in props:
            await self._port.handle_event(
                PlayerEvent(source=_SOURCE, metadata=_parse_track(props["Track"]))
            )
        if "Volume" in props:
            await self._port.handle_event(
                PlayerEvent(source=_SOURCE, volume=props["Volume"] / 127.0)
            )

    async def _media_transport_props_changed(self, props: dict) -> None:
        if "Volume" not in props:
            return
        raw: int | None = _v(props.get("Volume"))
        if raw is not None:
            await self._port.handle_event(
                PlayerEvent(source=_SOURCE, volume=raw / 127.0)
            )

    async def _fetch_volume(self, path: str, iface: str) -> None:
        if not self._bus:
            return
        try:
            reply = await self._bus.call(
                Message(
                    destination="org.bluez",
                    path=path,
                    interface="org.freedesktop.DBus.Properties",
                    member="Get",
                    signature="ss",
                    body=[iface, "Volume"],
                )
            )
            if not reply.body:
                return
            raw: int | None = _v(reply.body[0])
            if raw is not None:
                await self._port.handle_event(
                    PlayerEvent(source=_SOURCE, volume=raw / 127.0)
                )
        except Exception as e:
            _log.debug("BT volume Get failed (%s): %s", iface, e)

    async def _media_player_call(self, method: str) -> None:
        if not self._media_player_path or not self._bus:
            return
        try:
            await self._bus.call(
                Message(
                    destination="org.bluez",
                    path=self._media_player_path,
                    interface="org.bluez.MediaPlayer1",
                    member=method,
                )
            )
        except Exception as e:
            _log.debug("BT control %s failed: %s", method, e)

    async def play(self) -> None:
        await self._media_player_call("Play")

    async def pause(self) -> None:
        await self._media_player_call("Pause")

    async def stop(self) -> None:
        await self._media_player_call("Stop")

    async def next_track(self) -> None:
        await self._media_player_call("Next")

    async def previous_track(self) -> None:
        await self._media_player_call("Previous")
