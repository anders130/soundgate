from soundgate.adapters.sources.spotifyd import SpotifydAdapter

from .conftest import FakeEventPort, enc, make_adapter


class Callback:
    def __init__(self) -> None:
        self.calls = 0

    async def __call__(self) -> None:
        self.calls += 1


async def test_callback_fires_after_init_volumeset_suppressed(
    port: FakeEventPort,
) -> None:
    cb = Callback()
    adapter = SpotifydAdapter("/tmp/test.sock", port, on_init_suppressed=cb)
    await adapter._handle(enc(event="sessionconnected"))
    await adapter._handle(enc(event="volumeset", volume="7168"))
    assert cb.calls == 1


async def test_callback_not_fired_when_volumeset_passes_through(
    port: FakeEventPort,
) -> None:
    cb = Callback()
    adapter = SpotifydAdapter("/tmp/test.sock", port, on_init_suppressed=cb)
    await adapter._handle(enc(event="sessionconnected"))
    await adapter._handle(
        enc(event="volumeset", volume="7168")
    )  # suppressed → callback
    await adapter._handle(
        enc(event="volumeset", volume="32767")
    )  # different → passes through
    assert cb.calls == 1  # only from the suppressed one


async def test_callback_fires_only_once_per_session(port: FakeEventPort) -> None:
    cb = Callback()
    adapter = SpotifydAdapter("/tmp/test.sock", port, on_init_suppressed=cb)
    await adapter._handle(enc(event="sessionconnected"))
    await adapter._handle(enc(event="volumeset", volume="7168"))
    await adapter._handle(
        enc(event="volumeset", volume="7168")
    )  # same, still suppressed
    assert cb.calls == 1


async def test_callback_reset_on_new_session(port: FakeEventPort) -> None:
    cb = Callback()
    adapter = SpotifydAdapter("/tmp/test.sock", port, on_init_suppressed=cb)
    await adapter._handle(enc(event="sessionconnected"))
    await adapter._handle(enc(event="volumeset", volume="7168"))
    await adapter._handle(enc(event="sessiondisconnected"))
    await adapter._handle(enc(event="sessionconnected"))
    await adapter._handle(enc(event="volumeset", volume="9000"))
    assert cb.calls == 2


async def test_no_callback_when_none(port: FakeEventPort) -> None:
    adapter = make_adapter(port)  # no on_init_suppressed
    await adapter._handle(enc(event="sessionconnected"))
    await adapter._handle(enc(event="volumeset", volume="7168"))
    # must not raise
