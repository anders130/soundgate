from typing import Any

import pytest

from soundgate.domain.events import PlayerEvent


class FakeEventPort:
    def __init__(self) -> None:
        self.events: list[PlayerEvent] = []

    async def handle_event(self, event: PlayerEvent) -> None:
        self.events.append(event)


class FakeBus:
    def __init__(self) -> None:
        self.calls: list[Any] = []

    async def call(self, msg: Any) -> None:
        self.calls.append(msg)


@pytest.fixture
def port() -> FakeEventPort:
    return FakeEventPort()


@pytest.fixture
def bus() -> FakeBus:
    return FakeBus()
