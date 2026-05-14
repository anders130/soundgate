import pytest
from httpx import AsyncClient

from .conftest import FakeVolumePort


@pytest.mark.asyncio
async def test_post_volume_calls_set_volume(
    client: AsyncClient, volume_port: FakeVolumePort
) -> None:
    async with client as c:
        r = await c.post("/volume", json={"level": 0.6})
    assert r.status_code == 200
    assert volume_port.volumes == [0.6]


@pytest.mark.asyncio
async def test_post_volume_returns_ok(client: AsyncClient) -> None:
    async with client as c:
        r = await c.post("/volume", json={"level": 0.5})
    assert r.json() == {"ok": True}
