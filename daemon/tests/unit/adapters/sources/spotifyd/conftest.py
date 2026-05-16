import json

import pytest

from soundgate.adapters.sources.spotifyd import SpotifydAdapter
from soundgate.application.ports.inbound import PlayerEventPort
from soundgate.domain.events import PlayerEvent


class FakeEventPort(PlayerEventPort):
    def __init__(self) -> None:
        self.events: list[PlayerEvent] = []

    async def handle_event(self, event: PlayerEvent) -> None:
        self.events.append(event)


@pytest.fixture
def port() -> FakeEventPort:
    return FakeEventPort()


def make_adapter(port: FakeEventPort) -> SpotifydAdapter:
    return SpotifydAdapter("/tmp/test.sock", port)


def enc(**fields: str) -> bytes:
    base: dict[str, str] = {
        "event": "",
        "name": "",
        "artists": "",
        "album": "",
        "duration_ms": "",
        "volume": "",
        "position_ms": "",
        "track_id": "",
        "cover_url": "",
    }
    base.update(fields)
    return json.dumps(base).encode()
