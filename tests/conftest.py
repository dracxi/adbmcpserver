"""Pytest configuration and shared fixtures."""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_data_dir():
    """Return path to test data directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def sample_workflows_file(test_data_dir):
    """Return path to sample workflows file."""
    return test_data_dir / "sample_workflows.yaml"


@pytest.fixture
def mock_device_id():
    """Return mock device ID for testing."""
    return "test_device_12345"


@pytest.fixture
def mock_app_package():
    """Return mock app package name."""
    return "com.example.testapp"


# Markers for different test types
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers", "requires_device: Tests that require real Android device"
    )
