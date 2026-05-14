import pytest

from soundgate.adapters.sources.bluetooth import BluetoothAdapter

from .conftest import FakeEventPort


@pytest.mark.asyncio
async def test_seek_does_not_raise_without_player(port: FakeEventPort) -> None:
    adapter = BluetoothAdapter(port)
    await adapter.seek(30.0)
