import pytest
from httpx import AsyncClient, ASGITransport

from backend.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def authenticated_client(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "securepassword123",
            "full_name": "New User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"


@pytest.mark.asyncio
async def test_login(client):
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "loginuser@example.com",
            "password": "password123",
            "full_name": "Login User"
        }
    )
    
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_get_current_user(authenticated_client):
    response = await authenticated_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "role" in data


@pytest.mark.asyncio
async def test_list_projects_unauthorized(client):
    response = await client.get("/api/v1/projects")
    assert response.status_code == 401
