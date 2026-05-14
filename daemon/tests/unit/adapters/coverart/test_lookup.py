import re
from unittest.mock import AsyncMock, patch

import pytest
from aioresponses import aioresponses

import soundgate.adapters.coverart as m
from soundgate.adapters.coverart import lookup_art

_MB_URL = re.compile(r"https://musicbrainz\.org/ws/2/release.*")


@pytest.fixture(autouse=True)
def reset():
    m._cache.clear()
    m._cache_loaded = False
    m._last_request = 0.0
    m._rate_lock = None
    yield
    m._cache.clear()
    m._cache_loaded = False


async def test_cache_hit_skips_fetch():
    m._cache_loaded = True
    m._cache["beatles\x00abbey road"] = "http://cached.jpg"
    with patch.object(m, "_fetch", new=AsyncMock()) as mock_fetch:
        result = await lookup_art("Beatles", "Abbey Road")
    mock_fetch.assert_not_called()
    assert result == "http://cached.jpg"


async def test_cache_miss_calls_fetch_and_stores():
    m._cache_loaded = True
    with patch.object(
        m, "_fetch", new=AsyncMock(return_value="http://art.jpg")
    ) as mock_fetch:
        result = await lookup_art("Beatles", "Abbey Road")
    mock_fetch.assert_called_once_with("Beatles", "Abbey Road")
    assert result == "http://art.jpg"
    assert m._cache["beatles\x00abbey road"] == "http://art.jpg"


async def test_second_call_uses_cache():
    m._cache_loaded = True
    with patch.object(
        m, "_fetch", new=AsyncMock(return_value="http://art.jpg")
    ) as mock_fetch:
        await lookup_art("Beatles", "Abbey Road")
        await lookup_art("Beatles", "Abbey Road")
    mock_fetch.assert_called_once()


async def test_none_result_cached():
    m._cache_loaded = True
    with patch.object(m, "_fetch", new=AsyncMock(return_value=None)) as mock_fetch:
        r1 = await lookup_art("Unknown", "Unknown")
        r2 = await lookup_art("Unknown", "Unknown")
    mock_fetch.assert_called_once()
    assert r1 is None
    assert r2 is None


async def test_fetch_returns_caa_url():
    with aioresponses() as mocked:
        mocked.get(_MB_URL, payload={"releases": [{"id": "mbid-123"}]})
        result = await m._fetch("Beatles", "Abbey Road")
    assert result == "https://coverartarchive.org/release/mbid-123/front"


async def test_fetch_no_releases_returns_none():
    with aioresponses() as mocked:
        mocked.get(_MB_URL, payload={"releases": []})
        result = await m._fetch("Unknown", "Unknown")
    assert result is None


async def test_fetch_network_error_returns_none():
    with aioresponses() as mocked:
        mocked.get(_MB_URL, exception=Exception("timeout"))
        result = await m._fetch("Beatles", "Abbey Road")
    assert result is None
