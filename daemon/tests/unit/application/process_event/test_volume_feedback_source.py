from soundgate.application.use_cases.process_event import ProcessEventUseCase
from soundgate.domain.aggregator import AggregatorService
from soundgate.domain.events import PlayerEvent

from ..conftest import FakeVolumePort


class SourceCapturingFeedback:
    def __init__(self) -> None:
        self.calls: list[tuple[float, str | None]] = []

    async def sync_volume(self, level: float, source: str | None = None) -> None:
        self.calls.append((level, source))


def make_use_case(volume_port: FakeVolumePort) -> ProcessEventUseCase:
    return ProcessEventUseCase(
        sources={},
        aggregator=AggregatorService(),
        priority_map={},
        volume_port=volume_port,
    )


async def test_handle_event_passes_source_to_feedback(
    volume_port: FakeVolumePort,
) -> None:
    uc = make_use_case(volume_port)
    fb = SourceCapturingFeedback()
    uc.register_volume_feedback(fb)
    await uc.handle_event(PlayerEvent(source="spotify", volume=0.5))
    assert fb.calls == [(pytest.approx(0.5), "spotify")]


async def test_set_volume_passes_none_source_to_feedback(
    volume_port: FakeVolumePort,
) -> None:
    uc = make_use_case(volume_port)
    fb = SourceCapturingFeedback()
    uc.register_volume_feedback(fb)
    await uc.set_volume(0.5)
    assert fb.calls == [(pytest.approx(0.5), None)]


async def test_bluetooth_source_forwarded(volume_port: FakeVolumePort) -> None:
    uc = make_use_case(volume_port)
    fb = SourceCapturingFeedback()
    uc.register_volume_feedback(fb)
    await uc.handle_event(PlayerEvent(source="bluetooth", volume=0.3))
    assert fb.calls[0][1] == "bluetooth"


import pytest
