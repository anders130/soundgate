from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, POLL_INTERVAL

_log = logging.getLogger(__name__)


class SoundgateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, host: str, port: int) -> None:
        super().__init__(
            hass,
            _log,
            name=DOMAIN,
            update_interval=timedelta(seconds=POLL_INTERVAL),
        )
        self._url = f"http://{host}:{port}"
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            async with self._session.get(
                f"{self._url}/state",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"HTTP {resp.status}")
                return await resp.json()
        except aiohttp.ClientError as e:
            raise UpdateFailed(f"Connection error: {e}") from e

    async def async_post(self, path: str, json: dict | None = None) -> None:
        try:
            await self._session.post(
                f"{self._url}{path}",
                json=json or {},
                timeout=aiohttp.ClientTimeout(total=3),
            )
        except aiohttp.ClientError as e:
            _log.debug("POST %s failed: %s", path, e)
