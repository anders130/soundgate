import pytest

from .conftest import FakeEventPort, enc, make_adapter


async def test_volume_before_playback_emits_no_event(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="volume_changed", volume="65535"))
    assert port.events == []


async def test_volume_after_playing_emitted(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="playing", position_ms="0"))
    port.events.clear()
    await adapter._handle(enc(event="volume_changed", volume="65535"))
    assert port.events[-1].volume == pytest.approx(1.0)


async def test_volume_normalized_after_playing(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="playing", position_ms="0"))
    port.events.clear()
    await adapter._handle(enc(event="volume_changed", volume="32767"))
    assert port.events[-1].volume == pytest.approx(32767 / 65535)


async def test_volume_no_state(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="playing", position_ms="0"))
    port.events.clear()
    await adapter._handle(enc(event="volume_changed", volume="32767"))
    assert port.events[-1].state is None


async def test_volume_accepted_while_stopped(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="playing", position_ms="0"))
    await adapter._handle(enc(event="stopped"))
    port.events.clear()
    await adapter._handle(enc(event="volume_changed", volume="32767"))
    assert port.events[-1].volume == pytest.approx(32767 / 65535)


async def test_volume_reset_after_session_client_changed(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="playing", position_ms="0"))
    await adapter._handle(enc(event="session_client_changed"))
    port.events.clear()
    await adapter._handle(enc(event="volume_changed", volume="65535"))
    assert port.events == []


async def test_volume_reset_after_session_disconnected(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="playing", position_ms="0"))
    await adapter._handle(enc(event="session_disconnected"))
    port.events.clear()
    await adapter._handle(enc(event="volume_changed", volume="65535"))
    assert port.events == []


async def test_volume_after_started_but_before_playing_ignored(
    port: FakeEventPort,
) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="started"))
    port.events.clear()
    await adapter._handle(enc(event="volume_changed", volume="65535"))
    assert port.events == []


async def test_volume_accepted_after_playing_not_just_started(
    port: FakeEventPort,
) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="started"))
    await adapter._handle(enc(event="playing", position_ms="0"))
    port.events.clear()
    await adapter._handle(enc(event="volume_changed", volume="32767"))
    assert port.events[-1].volume == pytest.approx(32767 / 65535)
