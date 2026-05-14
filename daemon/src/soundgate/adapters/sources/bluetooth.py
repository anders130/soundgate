from soundgate.domain.events import Metadata, PlaybackState, PlayerEvent

_SOURCE = "bluetooth"
_BT_STATE_MAP: dict[str, PlaybackState] = {
    "playing": PlaybackState.PLAYING,
    "paused": PlaybackState.PAUSED,
    "stopped": PlaybackState.STOPPED,
    "forward-seek": PlaybackState.PLAYING,
    "reverse-seek": PlaybackState.PLAYING,
    "error": PlaybackState.STOPPED,
}


def _parse_track(track: dict) -> Metadata:
    def _str(val: str | None) -> str | None:
        return val if val else None

    duration = track.get("Duration")
    return Metadata(
        title=_str(track.get("Title")),
        artist=_str(track.get("Artist")),
        album=_str(track.get("Album")),
        art_url=_str(track.get("ArtUrl")),
        duration_us=duration * 1000 if duration is not None else None,
        track_id=track.get("TrackId"),
    )


class BluetoothAdapter:
    def __init__(self, event_port) -> None:
        self._port = event_port
        self._connected: set[str] = set()

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

    async def _device_connected(self, path: str, props: dict) -> None:
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

    async def _media_transport_props_changed(self, path: str, props: dict) -> None:
        if "Volume" in props:
            await self._port.handle_event(
                PlayerEvent(source=_SOURCE, volume=props["Volume"] / 127.0)
            )

    async def run(self) -> None:
        from dbus_fast import BusType
        from dbus_fast.aio import MessageBus

        bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
        # D-Bus signal wiring goes here
        await bus.wait_for_disconnect()
