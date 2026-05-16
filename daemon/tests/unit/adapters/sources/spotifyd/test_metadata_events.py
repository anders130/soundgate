from .conftest import FakeEventPort, enc, make_adapter


async def test_change_extracts_title(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="change", name="Comfortably Numb"))
    assert port.events[-1].metadata is not None
    assert port.events[-1].metadata.title == "Comfortably Numb"


async def test_change_extracts_artist(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="change", name="x", artists="Pink Floyd"))
    assert port.events[-1].metadata is not None
    assert port.events[-1].metadata.artist == "Pink Floyd"


async def test_change_extracts_album(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="change", name="x", album="The Wall"))
    assert port.events[-1].metadata is not None
    assert port.events[-1].metadata.album == "The Wall"


async def test_change_extracts_cover_url(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(
        enc(event="change", name="x", cover_url="https://i.scdn.co/image/abc")
    )
    assert port.events[-1].metadata is not None
    assert port.events[-1].metadata.art_url == "https://i.scdn.co/image/abc"


async def test_change_duration_ms_to_us(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="change", name="x", duration_ms="382000"))
    assert port.events[-1].metadata is not None
    assert port.events[-1].metadata.duration_us == 382_000_000


async def test_change_extracts_track_id(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(
        enc(event="change", name="x", track_id="spotify:track:abc123")
    )
    assert port.events[-1].metadata is not None
    assert port.events[-1].metadata.track_id == "spotify:track:abc123"


async def test_change_no_state(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="change", name="Song"))
    assert port.events[-1].state is None


async def test_empty_name_becomes_none(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="change", name="", artists="Pink Floyd"))
    assert port.events[-1].metadata is not None
    assert port.events[-1].metadata.title is None


async def test_empty_artists_becomes_none(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="change", name="Song", artists=""))
    assert port.events[-1].metadata is not None
    assert port.events[-1].metadata.artist is None


async def test_empty_duration_ms_becomes_none(port: FakeEventPort) -> None:
    adapter = make_adapter(port)
    await adapter._handle(enc(event="change", name="Song", duration_ms=""))
    assert port.events[-1].metadata is not None
    assert port.events[-1].metadata.duration_us is None
