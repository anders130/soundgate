import pytest

from .conftest import FakeEventPort, enc, make_adapter


async def test_first_volumeset_suppressed(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="volumeset", volume="7168"))
    assert port.events == []


async def test_second_volumeset_same_value_suppressed(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="volumeset", volume="7168"))
    await adapter._handle(enc(event="start"))
    port.events.clear()
    await adapter._handle(enc(event="volumeset", volume="7168"))
    assert all(e.volume is None for e in port.events)


async def test_different_value_after_init_accepted(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="volumeset", volume="7168"))
    await adapter._handle(enc(event="start"))
    port.events.clear()
    await adapter._handle(enc(event="volumeset", volume="32767"))
    assert port.events[-1].volume == pytest.approx(32767 / 65535)


async def test_init_guard_cleared_after_user_change(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="volumeset", volume="7168"))
    await adapter._handle(enc(event="volumeset", volume="32767"))  # user changes
    port.events.clear()
    await adapter._handle(enc(event="volumeset", volume="7168"))  # back to init value
    assert port.events[-1].volume == pytest.approx(7168 / 65535)


async def test_sessionconnected_resets_init_guard(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="volumeset", volume="7168"))  # init = 7168
    await adapter._handle(enc(event="sessionconnected"))
    await adapter._handle(
        enc(event="volumeset", volume="32767")
    )  # new session init = 32767
    port.events.clear()
    await adapter._handle(
        enc(event="volumeset", volume="7168")
    )  # different from new init
    assert port.events[-1].volume == pytest.approx(7168 / 65535)


async def test_volumeset_no_state(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="volumeset", volume="7168"))  # suppressed (init)
    await adapter._handle(enc(event="volumeset", volume="32767"))  # accepted
    assert port.events[-1].state is None


async def test_volume_empty_ignored(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="volumeset", volume="7168"))  # init
    await adapter._handle(enc(event="volumeset", volume=""))
    assert port.events == []
