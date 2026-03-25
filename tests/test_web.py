import pytest
from httpx import ASGITransport, AsyncClient

from app.web import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_form_page(client):
    r = await client.get("/")
    assert r.status_code == 200
    assert "Germany Café Navigator" in r.text
    assert "<form" in r.text


@pytest.mark.asyncio
async def test_evaluate_berlin(client):
    r = await client.post(
        "/api/evaluate",
        json={
            "state": "Berlin",
            "city": "Berlin",
            "serves_alcohol": False,
            "existing_gastro_premises": False,
            "employees_handle_food": True,
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert "summary" in data
    assert "must_do_now" in data
    assert len(data["must_do_now"]) >= 4
    assert "case_id" in data


@pytest.mark.asyncio
async def test_evaluate_nrw(client):
    r = await client.post(
        "/api/evaluate",
        json={
            "state": "NRW",
            "city": "Köln",
            "serves_alcohol": True,
            "existing_gastro_premises": False,
            "employees_handle_food": True,
            "legal_form": "GmbH",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data["must_do_now"]) >= 4
    assert len(data["conditional_steps"]) >= 1
    assert any("Gaststättenerlaubnis" in s for s in data["conditional_steps"])


@pytest.mark.asyncio
async def test_case_retrieval(client):
    r = await client.post(
        "/api/evaluate",
        json={
            "state": "Berlin",
            "city": "Berlin",
        },
    )
    case_id = r.json()["case_id"]

    r2 = await client.get(f"/api/cases/{case_id}")
    assert r2.status_code == 200
    assert r2.json()["must_do_now"] == r.json()["must_do_now"]


@pytest.mark.asyncio
async def test_case_not_found(client):
    r = await client.get("/api/cases/nonexistent")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_chat_api(client):
    r = await client.post("/api/chat", json={"message": "What is a Gewerbeanmeldung?"})
    assert r.status_code == 200
    data = r.json()
    assert "response" in data
    assert len(data["response"]) > 0


@pytest.mark.asyncio
async def test_invalid_input(client):
    r = await client.post(
        "/api/evaluate",
        json={
            "state": "InvalidState",
            "city": "Berlin",
        },
    )
    assert r.status_code == 422
