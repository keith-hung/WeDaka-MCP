"""Pytest configuration for WeDaka MCP Server tests"""

import os
import pytest
from dotenv import load_dotenv


def pytest_configure(config):
    """Configure pytest"""
    # Load test environment variables from .env.test if it exists
    test_env_path = os.path.join(os.path.dirname(__file__), '..', '.env.test')
    if os.path.exists(test_env_path):
        load_dotenv(test_env_path)
    
    # Also try loading from .env
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture"""
    return {
        "api_url": os.getenv("WEDAKA_API_URL"),
        "username": os.getenv("WEDAKA_USERNAME"),
        "device_id": os.getenv("WEDAKA_DEVICE_ID"),
        "emp_no": os.getenv("WEDAKA_EMP_NO"),
        "timeout": int(os.getenv("TEST_TIMEOUT", "30")),
        "verbose": os.getenv("TEST_VERBOSE", "false").lower() == "true"
    }


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Mark tests that require environment variables
        if "test_api" in item.nodeid or "integration" in item.nodeid:
            item.add_marker(pytest.mark.requires_env)