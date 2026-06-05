import asyncio

import pytest
from httpx import AsyncClient

from backend.main import create_app


@pytest.mark.asyncio
async def test_scene_describe_health() -> None:
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
