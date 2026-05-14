import pytest
from httpx import AsyncClient

from soundgate.application.use_cases.process_event import ProcessEventUseCase
from soundgate.domain.events import PlaybackState, PlayerEvent


@pytest.mark.asyncio
async def test_select_known_source_returns_ok(
    client: AsyncClient, process: ProcessEventUseCase
) -> None:
    await process.handle_event(
        PlayerEvent(source="bluetooth", state=PlaybackState.PAUSED)
    )
    async with client as c:
        r = await c.post("/source", json={"name": "bluetooth"})
    assert r.json()["ok"] is True


@pytest.mark.asyncio
async def test_select_unknown_source_returns_404(client: AsyncClient) -> None:
    async with client as c:
        r = await c.post("/source", json={"name": "unknown"})
    assert r.status_code == 404
