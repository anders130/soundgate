import pytest

from .conftest import FakeEventPort, enc, make_adapter


async def test_volume_max_becomes_one(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="volume_changed", volume="65535"))
    assert port.events[-1].volume == pytest.approx(1.0)


async def test_volume_zero_becomes_zero(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="volume_changed", volume="0"))
    assert port.events[-1].volume == pytest.approx(0.0)


async def test_volume_midpoint_normalized(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="volume_changed", volume="32767"))
    assert port.events[-1].volume == pytest.approx(32767 / 65535)


async def test_volume_no_state(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="volume_changed", volume="32767"))
    assert port.events[-1].state is None
