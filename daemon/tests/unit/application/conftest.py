import pytest
from soundgate.application.snapshot import Snapshot


class FakeVolumePort:
    def __init__(self) -> None:
        self.volumes: list[float] = []

    async def set_volume(self, level: float) -> None:
        self.volumes.append(level)

    async def get_volume(self) -> float:
        return self.volumes[-1] if self.volumes else 1.0


class FakeStateExportPort:
    def __init__(self) -> None:
        self.snapshots: list[Snapshot] = []

    async def publish(self, snapshot: Snapshot) -> None:
        self.snapshots.append(snapshot)


@pytest.fixture
def volume_port() -> FakeVolumePort:
    return FakeVolumePort()


@pytest.fixture
def state_sink() -> FakeStateExportPort:
    return FakeStateExportPort()
