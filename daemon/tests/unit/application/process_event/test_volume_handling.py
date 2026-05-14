import pytest
from soundgate.application.use_cases.process_event import ProcessEventUseCase
from soundgate.domain.aggregator import AggregatorService
from soundgate.domain.events import PlayerEvent

from ..conftest import FakeVolumePort


def make_use_case(volume_port: FakeVolumePort) -> ProcessEventUseCase:
    return ProcessEventUseCase(
        sources={},
        aggregator=AggregatorService(),
        priority_map={"bluetooth": 0},
        volume_port=volume_port,
    )


@pytest.mark.asyncio
async def test_volume_event_calls_volume_port(volume_port: FakeVolumePort) -> None:
    uc = make_use_case(volume_port)
    await uc.handle_event(PlayerEvent(source="bluetooth", volume=0.7))
    assert volume_port.volumes == [0.7]


@pytest.mark.asyncio
async def test_volume_is_set_before_snapshot_published(
    volume_port: FakeVolumePort,
) -> None:
    from ..conftest import FakeStateExportPort

    uc = make_use_case(volume_port)
    sink = FakeStateExportPort()
    uc.register_sink(sink)
    await uc.handle_event(PlayerEvent(source="bluetooth", volume=0.6))
    assert sink.snapshots[0].volume == 0.6


@pytest.mark.asyncio
async def test_event_without_volume_does_not_call_volume_port(
    volume_port: FakeVolumePort,
) -> None:
    uc = make_use_case(volume_port)
    await uc.handle_event(PlayerEvent(source="bluetooth"))
    assert volume_port.volumes == []


def test_volume_property_defaults_to_one(volume_port: FakeVolumePort) -> None:
    uc = make_use_case(volume_port)
    assert uc.volume == 1.0


@pytest.mark.asyncio
async def test_set_volume_calls_volume_port(volume_port: FakeVolumePort) -> None:
    uc = make_use_case(volume_port)
    await uc.set_volume(0.5)
    assert volume_port.volumes == [0.5]


@pytest.mark.asyncio
async def test_set_volume_clamps_and_updates_property(
    volume_port: FakeVolumePort,
) -> None:
    uc = make_use_case(volume_port)
    await uc.set_volume(1.5)
    assert uc.volume == 1.0


@pytest.mark.asyncio
async def test_set_volume_publishes_snapshot(volume_port: FakeVolumePort) -> None:
    from ..conftest import FakeStateExportPort

    uc = make_use_case(volume_port)
    sink = FakeStateExportPort()
    uc.register_sink(sink)
    await uc.set_volume(0.3)
    assert sink.snapshots[-1].volume == 0.3
