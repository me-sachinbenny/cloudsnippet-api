"""
Test cases for the tools router endpoints.

This module contains test cases for all CRUD operations and edge cases
in the tools router. It uses pytest-asyncio for async testing and
pytest fixtures for dependency injection and database setup.
"""

import pytest
from httpx import AsyncClient
from bson import ObjectId
from datetime import datetime
from typing import Dict, Any

from app.main import app
from app.models.tool_models import Tool
from app.infrastructure.database.mongodb import get_db

#-----------------------------------------------------------------------------
# Fixtures
#-----------------------------------------------------------------------------

@pytest.fixture
async def test_client():
    """Create a test client for making HTTP requests."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def sample_tool_data() -> Dict[str, Any]:
    """Sample tool data for testing."""
    return {
        "name": "Docker",
        "description": "Containerization platform",
        "image": "https://example.com/docker.png",
        "overview": "Docker is a platform for developing...",
        "troubleshooting": ["Check logs", "Verify ports"],
        "best_practices": ["Use multi-stage builds"],
        "implementation": "docker run hello-world",
        "tags": ["containerization", "devops"]
    }

@pytest.fixture
async def created_tool(test_client, sample_tool_data) -> Dict[str, Any]:
    """Create a tool and return its data."""
    response = await test_client.post("/api/v1/tools/", json=sample_tool_data)
    return response.json()

#-----------------------------------------------------------------------------
# Create Operation Tests
#-----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_tool_success(test_client, sample_tool_data):
    """Test successful tool creation."""
    response = await test_client.post("/api/v1/tools/", json=sample_tool_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_tool_data["name"]
    assert data["description"] == sample_tool_data["description"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

@pytest.mark.asyncio
async def test_create_tool_missing_required_fields(test_client):
    """Test tool creation with missing required fields."""
    response = await test_client.post("/api/v1/tools/", json={})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any("name" in error["loc"] for error in data["detail"])
    assert any("description" in error["loc"] for error in data["detail"])

@pytest.mark.asyncio
async def test_create_tool_invalid_data(test_client, sample_tool_data):
    """Test tool creation with invalid data types."""
    invalid_data = sample_tool_data.copy()
    invalid_data["tags"] = "not-a-list"  # Should be a list
    response = await test_client.post("/api/v1/tools/", json=invalid_data)
    assert response.status_code == 422

#-----------------------------------------------------------------------------
# Read Operation Tests
#-----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_tools_success(test_client, created_tool):
    """Test listing tools with pagination."""
    response = await test_client.get("/api/v1/tools/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert len(data["items"]) > 0

@pytest.mark.asyncio
async def test_list_tools_pagination(test_client, sample_tool_data):
    """Test pagination parameters for tool listing."""
    # Create multiple tools
    for i in range(3):
        tool_data = sample_tool_data.copy()
        tool_data["name"] = f"Tool {i}"
        await test_client.post("/api/v1/tools/", json=tool_data)

    # Test pagination
    response = await test_client.get("/api/v1/tools/?skip=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 2

@pytest.mark.asyncio
async def test_get_tool_by_id_success(test_client, created_tool):
    """Test getting a specific tool by ID."""
    tool_id = created_tool["id"]
    response = await test_client.get(f"/api/v1/tools/{tool_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tool_id
    assert data["name"] == created_tool["name"]

@pytest.mark.asyncio
async def test_get_tool_by_id_not_found(test_client):
    """Test getting a non-existent tool."""
    fake_id = str(ObjectId())
    response = await test_client.get(f"/api/v1/tools/{fake_id}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_tool_by_slug_success(test_client, created_tool):
    """Test getting a tool by its slug."""
    response = await test_client.get(f"/api/v1/tools/slug/{created_tool['slug']}")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == created_tool["slug"]
    assert data["name"] == created_tool["name"]

@pytest.mark.asyncio
async def test_search_tools_by_text(test_client, created_tool):
    """Test searching tools by text."""
    response = await test_client.get("/api/v1/tools/search?q=docker")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0
    assert any("docker" in item["name"].lower() for item in data["items"])

@pytest.mark.asyncio
async def test_search_tools_by_tag(test_client, created_tool):
    """Test searching tools by tag."""
    response = await test_client.get("/api/v1/tools/search?tag=devops")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0
    assert "devops" in created_tool["tags"]

#-----------------------------------------------------------------------------
# Update Operation Tests
#-----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_tool_success(test_client, created_tool):
    """Test successful tool update."""
    update_data = {
        "description": "Updated description",
        "best_practices": ["New best practice"]
    }
    response = await test_client.put(
        f"/api/v1/tools/{created_tool['id']}", 
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == update_data["description"]
    assert data["best_practices"] == update_data["best_practices"]
    assert data["updated_at"] > created_tool["updated_at"]

@pytest.mark.asyncio
async def test_update_tool_not_found(test_client):
    """Test updating a non-existent tool."""
    fake_id = str(ObjectId())
    response = await test_client.put(
        f"/api/v1/tools/{fake_id}", 
        json={"description": "Updated"}
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_tool_invalid_data(test_client, created_tool):
    """Test updating a tool with invalid data."""
    invalid_data = {"tags": "not-a-list"}  # Should be a list
    response = await test_client.put(
        f"/api/v1/tools/{created_tool['id']}", 
        json=invalid_data
    )
    assert response.status_code == 422

#-----------------------------------------------------------------------------
# Delete Operation Tests
#-----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_tool_success(test_client, created_tool):
    """Test successful tool deletion."""
    response = await test_client.delete(f"/api/v1/tools/{created_tool['id']}")
    assert response.status_code == 204

    # Verify tool is deleted
    get_response = await test_client.get(f"/api/v1/tools/{created_tool['id']}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_tool_not_found(test_client):
    """Test deleting a non-existent tool."""
    fake_id = str(ObjectId())
    response = await test_client.delete(f"/api/v1/tools/{fake_id}")
    assert response.status_code == 404

#-----------------------------------------------------------------------------
# Edge Case Tests
#-----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_duplicate_tool_name(test_client, created_tool):
    """Test creating a tool with a duplicate name."""
    duplicate_data = {
        "name": created_tool["name"],
        "description": "Different description"
    }
    response = await test_client.post("/api/v1/tools/", json=duplicate_data)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_invalid_object_id_format(test_client):
    """Test endpoints with invalid ObjectId format."""
    invalid_id = "not-an-object-id"
    response = await test_client.get(f"/api/v1/tools/{invalid_id}")
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_search_with_special_characters(test_client):
    """Test search endpoint with special characters."""
    response = await test_client.get("/api/v1/tools/search?q=$pecial&Ch@rs")
    assert response.status_code == 200  # Should handle special chars gracefully

@pytest.mark.asyncio
async def test_pagination_invalid_values(test_client):
    """Test list endpoint with invalid pagination values."""
    response = await test_client.get("/api/v1/tools/?skip=-1&limit=0")
    assert response.status_code == 422  # Should validate pagination params
