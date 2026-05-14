import pytest

from .conftest import FakeEventPort, enc, make_adapter

_IGNORED = [
    "session_connected",
    "session_disconnected",
    "session_client_changed",
    "auto_play_changed",
    "filter_explicit_content_changed",
    "shuffle_changed",
    "repeat_changed",
    "play_request_id_changed",
    "preloading",
    "loading",
]


@pytest.mark.parametrize("event", _IGNORED)
async def test_lifecycle_event_ignored(port: FakeEventPort, event: str) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event=event))
    assert port.events == []


async def test_unknown_event_ignored(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="some_future_event"))
    assert port.events == []


async def test_invalid_json_ignored(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(b"not json")
    assert port.events == []


async def test_empty_payload_ignored(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(b"{}")
    assert port.events == []
