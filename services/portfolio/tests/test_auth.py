"""
Tests for authentication endpoints.

Covers the full registration and login flow including
edge cases: duplicate emails, wrong passwords, and
accessing protected endpoints with and without tokens.
"""

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """Health endpoint returns 200 with correct shape."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_new_user(client):
    """Registering with valid data creates a user and returns a token."""
    response = await client.post("/api/v1/auth/register", json={
        "email": "arkam@example.com",
        "full_name": "Arkam Mohammed",
        "password": "securepassword123",
    })
    assert response.status_code == 201
    data = response.json()
    assert "token" in data
    assert data["token"]["token_type"] == "bearer"
    assert data["user"]["email"] == "arkam@example.com"
    assert "hashed_password" not in data["user"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    """Registering with an existing email returns 409 Conflict."""
    payload = {
        "email": "duplicate@example.com",
        "full_name": "Test User",
        "password": "securepassword123",
    }
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_valid_credentials(client):
    """Login with correct credentials returns a token."""
    await client.post("/api/v1/auth/register", json={
        "email": "login_test@example.com",
        "full_name": "Login User",
        "password": "mypassword123",
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "login_test@example.com",
        "password": "mypassword123",
    })
    assert response.status_code == 200
    assert "token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    """Login with wrong password returns 401."""
    await client.post("/api/v1/auth/register", json={
        "email": "wrongpass@example.com",
        "full_name": "Test User",
        "password": "correctpassword",
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "wrongpass@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_authenticated(client):
    """Authenticated request to /me returns the current user."""
    reg = await client.post("/api/v1/auth/register", json={
        "email": "me_test@example.com",
        "full_name": "Me User",
        "password": "password123",
    })
    token = reg.json()["token"]["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me_test@example.com"


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client):
    """Request to /me without a token returns 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
