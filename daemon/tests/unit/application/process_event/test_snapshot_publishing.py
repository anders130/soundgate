import pytest
from soundgate.application.use_cases.process_event import ProcessEventUseCase
from soundgate.domain.aggregator import AggregatorService
from soundgate.domain.events import PlaybackState, PlayerEvent

from ..conftest import FakeStateExportPort, FakeVolumePort


def make_use_case(
    volume_port: FakeVolumePort, *sinks: FakeStateExportPort
) -> ProcessEventUseCase:
    uc = ProcessEventUseCase(
        sources={},
        aggregator=AggregatorService(),
        priority_map={"bluetooth": 0},
        volume_port=volume_port,
    )
    for sink in sinks:
        uc.register_sink(sink)
    return uc


@pytest.mark.asyncio
async def test_handle_event_publishes_snapshot(
    volume_port: FakeVolumePort, state_sink: FakeStateExportPort
) -> None:
    uc = make_use_case(volume_port, state_sink)
    await uc.handle_event(PlayerEvent(source="bluetooth"))
    assert len(state_sink.snapshots) == 1


@pytest.mark.asyncio
async def test_snapshot_contains_active_source(
    volume_port: FakeVolumePort, state_sink: FakeStateExportPort
) -> None:
    uc = make_use_case(volume_port, state_sink)
    await uc.handle_event(PlayerEvent(source="bluetooth", state=PlaybackState.PAUSED))
    assert state_sink.snapshots[-1].active is uc.sources["bluetooth"]


@pytest.mark.asyncio
async def test_snapshot_active_is_none_when_no_candidate(
    volume_port: FakeVolumePort, state_sink: FakeStateExportPort
) -> None:
    uc = make_use_case(volume_port, state_sink)
    await uc.handle_event(PlayerEvent(source="bluetooth"))
    assert state_sink.snapshots[-1].active is None


@pytest.mark.asyncio
async def test_all_sinks_receive_snapshot(volume_port: FakeVolumePort) -> None:
    sink_a, sink_b = FakeStateExportPort(), FakeStateExportPort()
    uc = make_use_case(volume_port, sink_a, sink_b)
    await uc.handle_event(PlayerEvent(source="bluetooth"))
    assert len(sink_a.snapshots) == 1
    assert len(sink_b.snapshots) == 1
