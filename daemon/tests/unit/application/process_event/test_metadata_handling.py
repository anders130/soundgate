import pytest
from soundgate.application.use_cases.process_event import ProcessEventUseCase
from soundgate.domain.aggregator import AggregatorService
from soundgate.domain.events import Metadata, PlayerEvent

from ..conftest import FakeVolumePort


def make_use_case(volume_port: FakeVolumePort) -> ProcessEventUseCase:
    return ProcessEventUseCase(
        sources={},
        aggregator=AggregatorService(),
        priority_map={"bluetooth": 0},
        volume_port=volume_port,
    )


@pytest.mark.asyncio
async def test_event_with_metadata_replaces_source_metadata(
    volume_port: FakeVolumePort,
) -> None:
    uc = make_use_case(volume_port)
    meta = Metadata(title="Song", artist="Artist")
    await uc.handle_event(PlayerEvent(source="bluetooth", metadata=meta))
    assert uc.sources["bluetooth"].metadata == meta


@pytest.mark.asyncio
async def test_event_without_metadata_preserves_existing(
    volume_port: FakeVolumePort,
) -> None:
    uc = make_use_case(volume_port)
    meta = Metadata(title="Song")
    await uc.handle_event(PlayerEvent(source="bluetooth", metadata=meta))
    await uc.handle_event(PlayerEvent(source="bluetooth"))
    assert uc.sources["bluetooth"].metadata == meta


@pytest.mark.asyncio
async def test_empty_metadata_replaces_existing(volume_port: FakeVolumePort) -> None:
    uc = make_use_case(volume_port)
    await uc.handle_event(
        PlayerEvent(source="bluetooth", metadata=Metadata(title="Song"))
    )
    await uc.handle_event(PlayerEvent(source="bluetooth", metadata=Metadata()))
    assert uc.sources["bluetooth"].metadata == Metadata()
