import pytest
from httpx import ASGITransport, AsyncClient
from soundgate.adapters.sinks.rest_api.app import build_app
from soundgate.application.use_cases.process_event import ProcessEventUseCase
from soundgate.application.use_cases.query_state import QueryStateUseCase
from soundgate.domain.aggregator import AggregatorService


class FakeVolumePort:
    def __init__(self) -> None:
        self.volumes: list[float] = []

    async def set_volume(self, level: float) -> None:
        self.volumes.append(level)

    async def get_volume(self) -> float:
        return self.volumes[-1] if self.volumes else 1.0


class FakeControl:
    def __init__(self) -> None:
        self.calls: list[str | tuple] = []

    async def play(self) -> None:
        self.calls.append("play")

    async def pause(self) -> None:
        self.calls.append("pause")

    async def stop(self) -> None:
        self.calls.append("stop")

    async def next_track(self) -> None:
        self.calls.append("next_track")

    async def previous_track(self) -> None:
        self.calls.append("previous_track")

    async def seek(self, position_s: float) -> None:
        self.calls.append(("seek", position_s))


@pytest.fixture
def sources() -> dict:
    return {}


@pytest.fixture
def volume_port() -> FakeVolumePort:
    return FakeVolumePort()


@pytest.fixture
def process(sources, volume_port) -> ProcessEventUseCase:
    return ProcessEventUseCase(
        sources=sources,
        aggregator=AggregatorService(),
        priority_map={"bluetooth": 0},
        volume_port=volume_port,
    )


@pytest.fixture
def query(sources) -> QueryStateUseCase:
    return QueryStateUseCase(sources=sources, aggregator=AggregatorService())


@pytest.fixture
def control() -> FakeControl:
    return FakeControl()


@pytest.fixture
def client(process, query, control) -> AsyncClient:
    app = build_app(
        query=query,
        process=process,
        control_map={"bluetooth": control},
    )
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
