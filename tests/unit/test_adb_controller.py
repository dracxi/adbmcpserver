"""Unit tests for ADB Controller."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from mcp_server.adb_controller import ADBController


class TestADBController:
    """Test suite for ADB Controller."""
    
    @pytest.fixture
    def adb_controller(self):
        """Create ADB controller instance for testing."""
        return ADBController(device_id="test_device")
    
    def test_init(self, adb_controller):
        """Test ADB controller initialization."""
        assert adb_controller.device_id == "test_device"
        assert adb_controller.timeout > 0
    
    @patch('subprocess.run')
    def test_execute_command_success(self, mock_run, adb_controller):
        """Test successful command execution."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="success output",
            stderr=""
        )
        
        result = adb_controller.execute_command(["shell", "ls"])
        
        assert result["success"] is True
        assert result["stdout"] == "success output"
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_execute_command_failure(self, mock_run, adb_controller):
        """Test failed command execution."""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="error message"
        )
        
        result = adb_controller.execute_command(["shell", "invalid"])
        
        assert result["success"] is False
        assert "error message" in result["stderr"]
    
    @patch('subprocess.run')
    def test_execute_command_timeout(self, mock_run, adb_controller):
        """Test command timeout handling."""
        mock_run.side_effect = TimeoutError("Command timed out")
        
        result = adb_controller.execute_command(["shell", "sleep", "100"])
        
        assert result["success"] is False
        assert "timeout" in result["error"].lower()
    
    @patch('subprocess.run')
    def test_get_device_info(self, mock_run, adb_controller):
        """Test device info retrieval."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Android 12\nPixel 6",
            stderr=""
        )
        
        info = adb_controller.get_device_info()
        
        assert info is not None
        assert "Android" in info or "Pixel" in info
    
    @patch('subprocess.run')
    def test_install_app(self, mock_run, adb_controller):
        """Test app installation."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Success",
            stderr=""
        )
        
        result = adb_controller.install_app("/path/to/app.apk")
        
        assert result["success"] is True
    
    @patch('subprocess.run')
    def test_uninstall_app(self, mock_run, adb_controller):
        """Test app uninstallation."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Success",
            stderr=""
        )
        
        result = adb_controller.uninstall_app("com.example.app")
        
        assert result["success"] is True
    
    @patch('subprocess.run')
    def test_take_screenshot(self, mock_run, adb_controller):
        """Test screenshot capture."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="",
            stderr=""
        )
        
        result = adb_controller.take_screenshot("/tmp/screenshot.png")
        
        assert result["success"] is True
    
    def test_invalid_device_id(self):
        """Test initialization with invalid device ID."""
        with pytest.raises(ValueError):
            ADBController(device_id="")
