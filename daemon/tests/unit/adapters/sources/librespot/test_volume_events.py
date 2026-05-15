import pytest

from .conftest import FakeEventPort, enc, make_adapter


async def test_volume_changed_emits_event(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="volume_changed", volume="65535"))
    assert port.events[-1].volume == pytest.approx(1.0)


async def test_volume_normalized(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="volume_changed", volume="32767"))
    assert port.events[-1].volume == pytest.approx(32767 / 65535)


async def test_volume_no_state(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="volume_changed", volume="32767"))
    assert port.events[-1].state is None


async def test_volume_accepted_before_play(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="volume_changed", volume="32767"))
    assert port.events[-1].volume == pytest.approx(32767 / 65535)


async def test_volume_accepted_while_stopped(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="playing", position_ms="0"))
    await adapter._handle(enc(event="stopped"))
    port.events.clear()
    await adapter._handle(enc(event="volume_changed", volume="32767"))
    assert port.events[-1].volume == pytest.approx(32767 / 65535)
