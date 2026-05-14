from __future__ import annotations

import asyncio
import json
import logging
import os
import time

import aiohttp

_log = logging.getLogger(__name__)

_MB_SEARCH = "https://musicbrainz.org/ws/2/release"
_CAA_FRONT = "https://coverartarchive.org/release/{mbid}/front"
_UA = "soundgate/1.0 (https://github.com/anders130/soundgate)"
_TIMEOUT = aiohttp.ClientTimeout(total=8)

_cache: dict[str, str | None] = {}
_cache_loaded = False
_last_request: float = 0.0
_rate_lock: asyncio.Lock | None = None


def _cache_file() -> str:
    return os.path.join(
        os.environ.get("SOUNDGATE_CACHE_DIR", "/var/cache/soundgate"),
        "coverart.json",
    )


def _key(artist: str, album: str) -> str:
    return f"{artist.lower().strip()}\x00{album.lower().strip()}"


def _get_lock() -> asyncio.Lock:
    global _rate_lock
    if _rate_lock is None:
        _rate_lock = asyncio.Lock()
    return _rate_lock


def _load_cache() -> None:
    global _cache_loaded
    if _cache_loaded:
        return
    _cache_loaded = True
    try:
        with open(_cache_file()) as f:
            _cache.update(json.load(f))
    except FileNotFoundError:
        pass
    except Exception as e:
        _log.warning("coverart: cache load failed: %s", e)


def _save_cache() -> None:
    try:
        path = _cache_file()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(_cache, f)
    except Exception as e:
        _log.warning("coverart: cache save failed: %s", e)


async def lookup_art(artist: str, album: str) -> str | None:
    _load_cache()
    k = _key(artist, album)
    if k in _cache:
        return _cache[k]

    async with _get_lock():
        if k in _cache:
            return _cache[k]

        global _last_request
        wait = 1.0 - (time.monotonic() - _last_request)
        if wait > 0:
            await asyncio.sleep(wait)
        _last_request = time.monotonic()

        result = await _fetch(artist, album)
        _cache[k] = result
        _save_cache()
        return result


async def _fetch(artist: str, album: str) -> str | None:
    try:
        async with aiohttp.ClientSession(headers={"User-Agent": _UA}) as session:
            async with session.get(
                _MB_SEARCH,
                params={
                    "query": f'artist:"{artist}" release:"{album}"',
                    "fmt": "json",
                    "limit": "1",
                },
                timeout=_TIMEOUT,
            ) as resp:
                data = await resp.json()

        releases = data.get("releases", [])
        if not releases:
            _log.debug("coverart: no MB release for %r / %r", artist, album)
            return None

        mbid = releases[0].get("id")
        if not mbid:
            return None

        url = _CAA_FRONT.format(mbid=mbid)
        _log.debug("coverart: %r / %r -> %s", artist, album, url)
        return url
    except Exception as e:
        _log.debug("coverart lookup failed: %s", e)
        return None
