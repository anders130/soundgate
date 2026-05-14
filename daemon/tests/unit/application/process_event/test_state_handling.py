import pytest
from soundgate.application.use_cases.process_event import ProcessEventUseCase
from soundgate.domain.aggregator import AggregatorService
from soundgate.domain.events import PlaybackState, PlayerEvent

from ..conftest import FakeVolumePort


def make_use_case(volume_port: FakeVolumePort) -> ProcessEventUseCase:
    return ProcessEventUseCase(
        sources={},
        aggregator=AggregatorService(),
        priority_map={"bluetooth": 0},
        volume_port=volume_port,
    )


@pytest.mark.asyncio
async def test_event_with_state_updates_source_state(
    volume_port: FakeVolumePort,
) -> None:
    uc = make_use_case(volume_port)
    await uc.handle_event(PlayerEvent(source="bluetooth", state=PlaybackState.PLAYING))
    assert uc.sources["bluetooth"].state == PlaybackState.PLAYING


@pytest.mark.asyncio
async def test_event_without_state_keeps_existing_state(
    volume_port: FakeVolumePort,
) -> None:
    uc = make_use_case(volume_port)
    await uc.handle_event(PlayerEvent(source="bluetooth", state=PlaybackState.PLAYING))
    await uc.handle_event(PlayerEvent(source="bluetooth"))
    assert uc.sources["bluetooth"].state == PlaybackState.PLAYING


@pytest.mark.asyncio
async def test_event_with_position_updates_source(volume_port: FakeVolumePort) -> None:
    uc = make_use_case(volume_port)
    await uc.handle_event(PlayerEvent(source="bluetooth", position_us=30_000_000))
    assert uc.sources["bluetooth"].position_us == 30_000_000


@pytest.mark.asyncio
async def test_event_without_state_updates_last_event_at(
    volume_port: FakeVolumePort,
) -> None:
    uc = make_use_case(volume_port)
    await uc.handle_event(PlayerEvent(source="bluetooth", state=PlaybackState.PLAYING))
    before = uc.sources["bluetooth"].last_event_at
    await uc.handle_event(PlayerEvent(source="bluetooth"))
    assert uc.sources["bluetooth"].last_event_at >= before  # type: ignore[operator]
