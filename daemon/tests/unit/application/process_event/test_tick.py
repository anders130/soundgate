import pytest
from soundgate.application.use_cases.process_event import ProcessEventUseCase
from soundgate.domain.aggregator import AggregatorService

from ..conftest import FakeStateExportPort, FakeVolumePort


@pytest.mark.asyncio
async def test_tick_publishes_snapshot(
    volume_port: FakeVolumePort, state_sink: FakeStateExportPort
) -> None:
    uc = ProcessEventUseCase(
        sources={},
        aggregator=AggregatorService(),
        priority_map={},
        volume_port=volume_port,
    )
    uc.register_sink(state_sink)
    await uc.tick()
    assert len(state_sink.snapshots) == 1
