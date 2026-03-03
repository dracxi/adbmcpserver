"""Unit tests for Device Manager."""
import pytest
from unittest.mock import Mock, patch
from mcp_server.device_manager import DeviceManager


class TestDeviceManager:
    """Test suite for Device Manager."""
    
    @pytest.fixture
    def device_manager(self):
        """Create device manager instance for testing."""
        return DeviceManager()
    
    @patch('subprocess.run')
    def test_list_devices(self, mock_run, device_manager):
        """Test listing connected devices."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="List of devices attached\ndevice1\tdevice\ndevice2\tdevice",
            stderr=""
        )
        
        devices = device_manager.list_devices()
        
        assert len(devices) == 2
        assert "device1" in devices
        assert "device2" in devices
    
    @patch('subprocess.run')
    def test_list_devices_empty(self, mock_run, device_manager):
        """Test listing devices when none connected."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="List of devices attached\n",
            stderr=""
        )
        
        devices = device_manager.list_devices()
        
        assert len(devices) == 0
    
    def test_select_device(self, device_manager):
        """Test selecting active device."""
        device_manager.select_device("test_device")
        
        assert device_manager.active_device == "test_device"
    
    def test_get_active_device(self, device_manager):
        """Test getting active device."""
        device_manager.active_device = "test_device"
        
        device = device_manager.get_active_device()
        
        assert device == "test_device"
    
    def test_get_active_device_none(self, device_manager):
        """Test getting active device when none selected."""
        device = device_manager.get_active_device()
        
        assert device is None
    
    @patch('subprocess.run')
    def test_auto_select_device(self, mock_run, device_manager):
        """Test auto-selecting device when only one connected."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="List of devices attached\ndevice1\tdevice",
            stderr=""
        )
        
        device_manager.auto_select_device()
        
        assert device_manager.active_device == "device1"
    
    @patch('subprocess.run')
    def test_auto_select_device_multiple(self, mock_run, device_manager):
        """Test auto-select fails with multiple devices."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="List of devices attached\ndevice1\tdevice\ndevice2\tdevice",
            stderr=""
        )
        
        with pytest.raises(ValueError):
            device_manager.auto_select_device()
    
    def test_is_device_connected(self, device_manager):
        """Test checking if device is connected."""
        device_manager.connected_devices = ["device1", "device2"]
        
        assert device_manager.is_device_connected("device1") is True
        assert device_manager.is_device_connected("device3") is False
    
    @patch('subprocess.run')
    def test_get_device_properties(self, mock_run, device_manager):
        """Test getting device properties."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="[ro.product.model]: [Pixel 6]\n[ro.build.version.release]: [12]",
            stderr=""
        )
        
        props = device_manager.get_device_properties("device1")
        
        assert props is not None
        assert "Pixel" in str(props) or "12" in str(props)
