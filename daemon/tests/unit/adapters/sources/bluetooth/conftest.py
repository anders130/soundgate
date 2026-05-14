import pytest

from soundgate.domain.events import PlayerEvent


class FakeEventPort:
    def __init__(self) -> None:
        self.events: list[PlayerEvent] = []

    async def handle_event(self, event: PlayerEvent) -> None:
        self.events.append(event)


@pytest.fixture
def port() -> FakeEventPort:
    return FakeEventPort()
