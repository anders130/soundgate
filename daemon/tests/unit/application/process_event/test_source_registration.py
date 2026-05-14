import pytest

from soundgate.application.use_cases.process_event import ProcessEventUseCase
from soundgate.domain.aggregator import AggregatorService
from soundgate.domain.events import PlayerEvent

from ..conftest import FakeVolumePort


def make_use_case(
    volume_port: FakeVolumePort, priority_map: dict
) -> ProcessEventUseCase:
    return ProcessEventUseCase(
        sources={},
        aggregator=AggregatorService(),
        priority_map=priority_map,
        volume_port=volume_port,
    )


@pytest.mark.asyncio
async def test_first_event_registers_source(volume_port: FakeVolumePort) -> None:
    uc = make_use_case(volume_port, {"bluetooth": 0})
    await uc.handle_event(PlayerEvent(source="bluetooth"))
    assert "bluetooth" in uc.sources


@pytest.mark.asyncio
async def test_registered_source_gets_priority_from_map(
    volume_port: FakeVolumePort,
) -> None:
    uc = make_use_case(volume_port, {"airplay": 0, "bluetooth": 1})
    await uc.handle_event(PlayerEvent(source="bluetooth"))
    assert uc.sources["bluetooth"].priority == 1


@pytest.mark.asyncio
async def test_unknown_source_gets_fallback_priority(
    volume_port: FakeVolumePort,
) -> None:
    uc = make_use_case(volume_port, {"airplay": 0, "bluetooth": 1})
    await uc.handle_event(PlayerEvent(source="dlna"))
    assert uc.sources["dlna"].priority == 2


@pytest.mark.asyncio
async def test_second_event_does_not_re_register_source(
    volume_port: FakeVolumePort,
) -> None:
    uc = make_use_case(volume_port, {"bluetooth": 0})
    await uc.handle_event(PlayerEvent(source="bluetooth"))
    original = uc.sources["bluetooth"]
    await uc.handle_event(PlayerEvent(source="bluetooth"))
    assert uc.sources["bluetooth"] is original
