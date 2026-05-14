from .conftest import FakeEventPort, enc, make_adapter


async def test_heartbeat_starts_on_playing(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="started"))
    assert adapter._heartbeat_task is not None
    assert not adapter._heartbeat_task.done()
    adapter._heartbeat_task.cancel()


async def test_heartbeat_stops_on_paused(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="started"))
    await adapter._handle(enc(event="paused", position_ms="1000"))
    assert adapter._heartbeat_task is None


async def test_heartbeat_stops_on_stopped(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="started"))
    await adapter._handle(enc(event="stopped"))
    assert adapter._heartbeat_task is None


async def test_heartbeat_not_started_twice(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="started"))
    task1 = adapter._heartbeat_task
    await adapter._handle(enc(event="playing", position_ms="1000"))
    assert adapter._heartbeat_task is task1
    assert task1 is not None
    task1.cancel()
