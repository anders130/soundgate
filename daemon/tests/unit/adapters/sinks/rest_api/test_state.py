import pytest
from httpx import AsyncClient
from soundgate.application.use_cases.process_event import ProcessEventUseCase
from soundgate.domain.events import Metadata, PlaybackState, PlayerEvent


@pytest.mark.asyncio
async def test_state_no_active_source_returns_stopped(client: AsyncClient) -> None:
    async with client as c:
        r = await c.get("/state")
    assert r.status_code == 200
    data = r.json()
    assert data["state"] == "stopped"
    assert data["source"] is None
    assert data["title"] is None


@pytest.mark.asyncio
async def test_state_includes_volume(
    client: AsyncClient, process: ProcessEventUseCase
) -> None:
    await process.set_volume(0.8)
    async with client as c:
        r = await c.get("/state")
    assert r.json()["volume"] == 0.8


@pytest.mark.asyncio
async def test_state_active_source_returns_metadata(
    client: AsyncClient, process: ProcessEventUseCase
) -> None:
    await process.handle_event(
        PlayerEvent(
            source="bluetooth",
            state=PlaybackState.PAUSED,
            metadata=Metadata(title="Song", artist="Artist", album="Album"),
        )
    )
    async with client as c:
        r = await c.get("/state")
    data = r.json()
    assert data["state"] == "paused"
    assert data["source"] == "bluetooth"
    assert data["title"] == "Song"
    assert data["artist"] == "Artist"
    assert data["album"] == "Album"


@pytest.mark.asyncio
async def test_state_converts_microseconds_to_seconds(
    client: AsyncClient, process: ProcessEventUseCase
) -> None:
    await process.handle_event(
        PlayerEvent(
            source="bluetooth",
            state=PlaybackState.PAUSED,
            metadata=Metadata(duration_us=90_000_000),
            position_us=30_000_000,
        )
    )
    async with client as c:
        r = await c.get("/state")
    data = r.json()
    assert data["duration_s"] == 90.0
    assert data["position_s"] == 30.0


@pytest.mark.asyncio
async def test_state_sources_list(
    client: AsyncClient, process: ProcessEventUseCase
) -> None:
    await process.handle_event(
        PlayerEvent(source="bluetooth", state=PlaybackState.PAUSED)
    )
    async with client as c:
        r = await c.get("/state")
    sources = r.json()["sources"]
    assert any(s["name"] == "bluetooth" for s in sources)
