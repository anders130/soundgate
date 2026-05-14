from __future__ import annotations

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import SoundgateCoordinator

_FEATURES_BASE = (
    MediaPlayerEntityFeature.VOLUME_SET | MediaPlayerEntityFeature.SELECT_SOURCE
)
_FEATURES_TRANSPORT = (
    _FEATURES_BASE
    | MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.STOP
    | MediaPlayerEntityFeature.SEEK
)
_FEATURES_FULL = (
    _FEATURES_TRANSPORT
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.PREVIOUS_TRACK
)

_UNCONTROLLABLE_SOURCES = {"spotify", "airplay"}
_TRANSPORT_ONLY_SOURCES = {"dlna"}

_STATE_MAP = {
    "playing": MediaPlayerState.PLAYING,
    "paused": MediaPlayerState.PAUSED,
    "stopped": MediaPlayerState.IDLE,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SoundgateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SoundgateMediaPlayer(coordinator, entry)])


class SoundgateMediaPlayer(CoordinatorEntity[SoundgateCoordinator], MediaPlayerEntity):
    _attr_has_entity_name = True
    _attr_name = None

    def __init__(
        self,
        coordinator: SoundgateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "soundgate",
        }

    @property
    def _data(self) -> dict:
        return self.coordinator.data or {}

    @property
    def state(self) -> MediaPlayerState:
        return _STATE_MAP.get(self._data.get("state", "stopped"), MediaPlayerState.IDLE)

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        src = self._data.get("source")
        if src in _UNCONTROLLABLE_SOURCES:
            return _FEATURES_BASE
        if src in _TRANSPORT_ONLY_SOURCES:
            return _FEATURES_TRANSPORT
        return _FEATURES_FULL

    @property
    def media_title(self) -> str | None:
        return self._data.get("title")

    @property
    def media_artist(self) -> str | None:
        return self._data.get("artist")

    @property
    def media_album_name(self) -> str | None:
        return self._data.get("album")

    @property
    def media_image_url(self) -> str | None:
        return self._data.get("art_url")

    @property
    def media_duration(self) -> float | None:
        return self._data.get("duration_s")

    @property
    def media_position(self) -> float | None:
        return self._data.get("position_s")

    @property
    def media_position_updated_at(self):
        return dt_util.utcnow()

    @property
    def volume_level(self) -> float | None:
        return self._data.get("volume")

    @property
    def source(self) -> str | None:
        return self._data.get("source")

    @property
    def source_list(self) -> list[str]:
        return [s["name"] for s in self._data.get("sources", [])]

    async def async_media_play(self) -> None:
        await self.coordinator.async_post("/play")

    async def async_media_pause(self) -> None:
        await self.coordinator.async_post("/pause")

    async def async_media_stop(self) -> None:
        await self.coordinator.async_post("/stop")

    async def async_media_next_track(self) -> None:
        await self.coordinator.async_post("/next")

    async def async_media_previous_track(self) -> None:
        await self.coordinator.async_post("/previous")

    async def async_set_volume_level(self, volume: float) -> None:
        await self.coordinator.async_post("/volume", {"level": volume})

    async def async_media_seek(self, position: float) -> None:
        await self.coordinator.async_post("/seek", {"position_s": position})

    async def async_select_source(self, source: str) -> None:
        await self.coordinator.async_post("/source", {"name": source})
