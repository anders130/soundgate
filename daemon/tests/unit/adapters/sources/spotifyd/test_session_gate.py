import pytest

from .conftest import FakeEventPort, enc, make_adapter


async def test_init_volume_suppressed_before_start(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="volumeset", volume="7168"))
    assert port.events == []


async def test_init_volume_suppressed_after_start(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="volumeset", volume="7168"))
    await adapter._handle(enc(event="start"))
    port.events.clear()
    await adapter._handle(enc(event="volumeset", volume="7168"))
    assert all(e.volume is None for e in port.events)


async def test_user_change_accepted_after_init(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="volumeset", volume="7168"))
    await adapter._handle(enc(event="start"))
    port.events.clear()
    await adapter._handle(enc(event="volumeset", volume="50000"))
    assert port.events[-1].volume == pytest.approx(50000 / 65535)


async def test_sessiondisconnected_resets_init_guard(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="volumeset", volume="7168"))
    await adapter._handle(enc(event="sessiondisconnected"))
    await adapter._handle(enc(event="volumeset", volume="9000"))  # new session init
    port.events.clear()
    await adapter._handle(enc(event="volumeset", volume="7168"))  # different → accepted
    assert port.events[-1].volume == pytest.approx(7168 / 65535)
