import pytest
from httpx import AsyncClient

PROGRAM_PAYLOAD = {
    "slug": "test-ausbildung",
    "title": "Test Ausbildung",
    "category": "ausbildung",
    "level": "beginner",
    "short_description": "A test vocational training program.",
    "description": "Full description of the test Ausbildung program.",
    "duration_months": 36,
    "min_age": 16,
    "max_age": 30,
    "language_requirement": "B1",
    "salary_range": "700-900 €",
    "is_published": True,
}


@pytest.mark.asyncio
async def test_create_program_as_admin(client: AsyncClient, admin_token: str):
    resp = await client.post(
        "/api/v1/programs",
        json=PROGRAM_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["slug"] == "test-ausbildung"
    assert data["category"] == "ausbildung"


@pytest.mark.asyncio
async def test_create_program_as_user_forbidden(client: AsyncClient, user_token: str):
    resp = await client.post(
        "/api/v1/programs",
        json=PROGRAM_PAYLOAD,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_list_programs(client: AsyncClient, admin_token: str):
    # Create a program first
    await client.post(
        "/api/v1/programs",
        json=PROGRAM_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    resp = await client.get("/api/v1/programs")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_get_program_by_slug(client: AsyncClient, admin_token: str):
    await client.post(
        "/api/v1/programs",
        json=PROGRAM_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    resp = await client.get("/api/v1/programs/test-ausbildung")
    assert resp.status_code == 200
    assert resp.json()["slug"] == "test-ausbildung"


@pytest.mark.asyncio
async def test_get_program_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/programs/non-existent-slug")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_program_as_admin(client: AsyncClient, admin_token: str):
    create_resp = await client.post(
        "/api/v1/programs",
        json=PROGRAM_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    program_id = create_resp.json()["id"]
    resp = await client.patch(
        f"/api/v1/programs/{program_id}",
        json={"title": "Updated Title"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_delete_program_as_admin(client: AsyncClient, admin_token: str):
    create_resp = await client.post(
        "/api/v1/programs",
        json=PROGRAM_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    program_id = create_resp.json()["id"]
    resp = await client.delete(
        f"/api/v1/programs/{program_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_filter_programs_by_category(client: AsyncClient, admin_token: str):
    await client.post(
        "/api/v1/programs",
        json=PROGRAM_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    resp = await client.get("/api/v1/programs?category=ausbildung")
    assert resp.status_code == 200
    for item in resp.json()["items"]:
        assert item["category"] == "ausbildung"
