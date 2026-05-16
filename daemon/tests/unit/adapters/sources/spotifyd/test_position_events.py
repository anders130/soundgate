from .conftest import FakeEventPort, enc, make_adapter


async def test_playing_position_ms_to_us(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="playing", position_ms="5000"))
    assert port.events[-1].position_us == 5_000_000


async def test_pause_position_ms_to_us(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="pause", position_ms="12345"))
    assert port.events[-1].position_us == 12_345_000


async def test_paused_position_ms_to_us(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="paused", position_ms="12345"))
    assert port.events[-1].position_us == 12_345_000


async def test_empty_position_ms_gives_none(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="playing", position_ms=""))
    assert port.events[-1].position_us is None
