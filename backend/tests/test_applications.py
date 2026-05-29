import pytest
from httpx import AsyncClient

PROGRAM_PAYLOAD = {
    "slug": "fsj-health",
    "title": "FSJ im Gesundheitswesen",
    "category": "fsj",
    "level": "beginner",
    "short_description": "Voluntary social year in the health sector.",
    "description": "Full description of the FSJ health program.",
    "is_published": True,
}


@pytest.mark.asyncio
async def test_apply_to_program(client: AsyncClient, admin_token: str, user_token: str):
    # Admin creates program
    create_resp = await client.post(
        "/api/v1/programs",
        json=PROGRAM_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    program_id = create_resp.json()["id"]

    # User applies
    resp = await client.post(
        "/api/v1/applications",
        json={"program_id": program_id, "motivation_letter": "I am very motivated!"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["program_id"] == program_id
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_apply_duplicate_rejected(client: AsyncClient, admin_token: str, user_token: str):
    create_resp = await client.post(
        "/api/v1/programs",
        json=PROGRAM_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    program_id = create_resp.json()["id"]
    payload = {"program_id": program_id}

    await client.post(
        "/api/v1/applications", json=payload,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    resp = await client.post(
        "/api/v1/applications", json=payload,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_list_my_applications(client: AsyncClient, admin_token: str, user_token: str):
    create_resp = await client.post(
        "/api/v1/programs",
        json=PROGRAM_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    program_id = create_resp.json()["id"]
    await client.post(
        "/api/v1/applications",
        json={"program_id": program_id},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    resp = await client.get(
        "/api/v1/applications/my",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


@pytest.mark.asyncio
async def test_admin_update_application_status(
    client: AsyncClient, admin_token: str, user_token: str
):
    create_resp = await client.post(
        "/api/v1/programs",
        json=PROGRAM_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    program_id = create_resp.json()["id"]
    apply_resp = await client.post(
        "/api/v1/applications",
        json={"program_id": program_id},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    app_id = apply_resp.json()["id"]

    resp = await client.patch(
        f"/api/v1/applications/{app_id}",
        json={"status": "approved", "admin_note": "Great candidate!"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "approved"
