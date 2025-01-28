import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch
from ..web5.data_manager import Web5DataManager, DWNRecord

@pytest.fixture
def web5_manager():
    return Web5DataManager(
        dwn_endpoint="https://dwn.example.com",
        did="did:example:123"
    )

@pytest.mark.asyncio
async def test_create_record(web5_manager):
    test_data = {"key": "value"}
    mock_response = {
        "id": "record123",
        "owner": web5_manager.did,
        "schema": "test-schema",
        "data": test_data,
        "created_at": "2025-01-28T13:56:40+02:00",
        "updated_at": "2025-01-28T13:56:40+02:00"
    }
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )
        mock_post.return_value.__aenter__.return_value.raise_for_status = AsyncMock()
        
        async with web5_manager:
            record = await web5_manager.create_record(
                schema="test-schema",
                data=test_data
            )
            
        assert record.id == "record123"
        assert record.owner == web5_manager.did
        assert record.data == test_data

@pytest.mark.asyncio
async def test_get_record(web5_manager):
    mock_response = {
        "id": "record123",
        "owner": web5_manager.did,
        "schema": "test-schema",
        "data": {"key": "value"},
        "created_at": "2025-01-28T13:56:40+02:00",
        "updated_at": "2025-01-28T13:56:40+02:00"
    }
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )
        mock_get.return_value.__aenter__.return_value.raise_for_status = AsyncMock()
        
        async with web5_manager:
            record = await web5_manager.get_record("record123")
            
        assert record.id == "record123"
        assert record.data["key"] == "value"

@pytest.mark.asyncio
async def test_query_records(web5_manager):
    mock_response = [{
        "id": f"record{i}",
        "owner": web5_manager.did,
        "schema": "test-schema",
        "data": {"key": f"value{i}"},
        "created_at": "2025-01-28T13:56:40+02:00",
        "updated_at": "2025-01-28T13:56:40+02:00"
    } for i in range(3)]
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )
        mock_get.return_value.__aenter__.return_value.raise_for_status = AsyncMock()
        
        async with web5_manager:
            records = await web5_manager.query_records(
                schema="test-schema",
                filter_={"key": "value1"}
            )
            
        assert len(records) == 3
        assert all(isinstance(r, DWNRecord) for r in records)

@pytest.mark.asyncio
async def test_update_record(web5_manager):
    test_data = {"key": "updated"}
    mock_response = {
        "id": "record123",
        "owner": web5_manager.did,
        "schema": "test-schema",
        "data": test_data,
        "created_at": "2025-01-28T13:56:40+02:00",
        "updated_at": "2025-01-28T13:56:40+02:00"
    }
    
    with patch("aiohttp.ClientSession.put") as mock_put:
        mock_put.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )
        mock_put.return_value.__aenter__.return_value.raise_for_status = AsyncMock()
        
        async with web5_manager:
            record = await web5_manager.update_record(
                "record123",
                test_data
            )
            
        assert record.data == test_data

@pytest.mark.asyncio
async def test_delete_record(web5_manager):
    with patch("aiohttp.ClientSession.delete") as mock_delete:
        mock_delete.return_value.__aenter__.return_value.raise_for_status = AsyncMock()
        
        async with web5_manager:
            await web5_manager.delete_record("record123")
            
        mock_delete.assert_called_once()
