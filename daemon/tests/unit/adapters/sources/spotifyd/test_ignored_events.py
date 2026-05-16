import pytest

from .conftest import FakeEventPort, enc, make_adapter

_IGNORED = [
    "some_future_event",
    "load",
    "preloading",
]


@pytest.mark.parametrize("event", _IGNORED)
async def test_unknown_event_ignored(port: FakeEventPort, event: str) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event=event))
    assert port.events == []


async def test_invalid_json_ignored(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(b"not json")
    assert port.events == []


async def test_empty_payload_ignored(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(b"{}")
    assert port.events == []
