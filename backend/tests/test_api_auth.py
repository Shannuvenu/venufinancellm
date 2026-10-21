import asyncio

import httpx

from app.config import settings
from app.main import app


def test_production_api_requires_the_server_to_server_token(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")
    monkeypatch.setattr(settings, "app_internal_token", "test-only-token")

    async def run_requests():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            blocked = await client.get("/api/health")
            allowed = await client.get("/api/health", headers={"X-Internal-API-Key": "test-only-token"})
            public_health = await client.get("/healthz")
        return blocked, allowed, public_health

    blocked, allowed, public_health = asyncio.run(run_requests())
    assert blocked.status_code == 401
    assert allowed.status_code == 200
    assert public_health.status_code == 200


def test_production_api_fails_closed_when_gateway_token_is_missing(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")
    monkeypatch.setattr(settings, "app_internal_token", "")

    async def run_request():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/api/health")

    response = asyncio.run(run_request())
    assert response.status_code == 503
