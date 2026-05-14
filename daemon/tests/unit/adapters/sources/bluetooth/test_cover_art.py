import asyncio
from unittest.mock import AsyncMock

import pytest

from soundgate.adapters.sources.bluetooth import BluetoothAdapter
from soundgate.domain.events import PlaybackState

from .conftest import FakeEventPort


async def test_track_with_artist_and_album_triggers_art_lookup(
    port: FakeEventPort,
) -> None:
    art_lookup = AsyncMock(return_value="http://art.jpg")
    adapter = BluetoothAdapter(port, art_lookup=art_lookup)
    await adapter._media_player_props_changed(
        {"Track": {"Title": "Song", "Artist": "Beatles", "Album": "Abbey Road"}}
    )
    await asyncio.sleep(0)
    art_lookup.assert_called_once_with("Beatles", "Abbey Road")


async def test_art_lookup_emits_followup_event(port: FakeEventPort) -> None:
    art_lookup = AsyncMock(return_value="http://art.jpg")
    adapter = BluetoothAdapter(port, art_lookup=art_lookup)
    await adapter._media_player_props_changed(
        {"Track": {"Title": "Song", "Artist": "Beatles", "Album": "Abbey Road"}}
    )
    await asyncio.sleep(0)
    urls = [
        e.metadata.art_url for e in port.events if e.metadata and e.metadata.art_url
    ]
    assert "http://art.jpg" in urls


async def test_no_artist_skips_art_lookup(port: FakeEventPort) -> None:
    art_lookup = AsyncMock(return_value="http://art.jpg")
    adapter = BluetoothAdapter(port, art_lookup=art_lookup)
    await adapter._media_player_props_changed({"Track": {"Title": "Song"}})
    await asyncio.sleep(0)
    art_lookup.assert_not_called()


async def test_art_lookup_none_emits_no_extra_event(port: FakeEventPort) -> None:
    art_lookup = AsyncMock(return_value=None)
    adapter = BluetoothAdapter(port, art_lookup=art_lookup)
    await adapter._media_player_props_changed(
        {"Track": {"Title": "Song", "Artist": "Beatles", "Album": "Abbey Road"}}
    )
    initial_count = len(port.events)
    await asyncio.sleep(0)
    assert len(port.events) == initial_count
