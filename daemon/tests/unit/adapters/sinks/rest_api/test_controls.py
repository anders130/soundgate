import pytest
from httpx import AsyncClient

from soundgate.application.use_cases.process_event import ProcessEventUseCase
from soundgate.domain.events import PlaybackState, PlayerEvent

from .conftest import FakeControl


async def activate_bluetooth(process: ProcessEventUseCase) -> None:
    await process.handle_event(
        PlayerEvent(source="bluetooth", state=PlaybackState.PAUSED)
    )


@pytest.mark.asyncio
async def test_play_calls_control(
    client: AsyncClient, process: ProcessEventUseCase, control: FakeControl
) -> None:
    await activate_bluetooth(process)
    async with client as c:
        await c.post("/play")
    assert "play" in control.calls


@pytest.mark.asyncio
async def test_pause_calls_control(
    client: AsyncClient, process: ProcessEventUseCase, control: FakeControl
) -> None:
    await activate_bluetooth(process)
    async with client as c:
        await c.post("/pause")
    assert "pause" in control.calls


@pytest.mark.asyncio
async def test_next_track_calls_control(
    client: AsyncClient, process: ProcessEventUseCase, control: FakeControl
) -> None:
    await activate_bluetooth(process)
    async with client as c:
        await c.post("/next")
    assert "next_track" in control.calls


@pytest.mark.asyncio
async def test_previous_track_calls_control(
    client: AsyncClient, process: ProcessEventUseCase, control: FakeControl
) -> None:
    await activate_bluetooth(process)
    async with client as c:
        await c.post("/previous")
    assert "previous_track" in control.calls


@pytest.mark.asyncio
async def test_seek_calls_control_with_position(
    client: AsyncClient, process: ProcessEventUseCase, control: FakeControl
) -> None:
    await activate_bluetooth(process)
    async with client as c:
        await c.post("/seek", json={"position_s": 42.0})
    assert ("seek", 42.0) in control.calls


@pytest.mark.asyncio
async def test_control_with_no_active_source_returns_not_ok(
    client: AsyncClient,
) -> None:
    async with client as c:
        r = await c.post("/play")
    assert r.json()["ok"] is False


@pytest.mark.asyncio
async def test_stop_calls_control(
    client: AsyncClient, process: ProcessEventUseCase, control: FakeControl
) -> None:
    await activate_bluetooth(process)
    async with client as c:
        await c.post("/stop")
    assert "stop" in control.calls
