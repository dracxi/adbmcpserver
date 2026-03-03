"""Unit tests for UI Controller."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from mcp_server.ui_controller import UIController


class TestUIController:
    """Test suite for UI Controller."""
    
    @pytest.fixture
    def ui_controller(self):
        """Create UI controller instance for testing."""
        with patch('uiautomator2.connect') as mock_connect:
            mock_device = Mock()
            mock_connect.return_value = mock_device
            controller = UIController(device_id="test_device")
            controller.device = mock_device
            return controller
    
    def test_init(self, ui_controller):
        """Test UI controller initialization."""
        assert ui_controller.device_id == "test_device"
        assert ui_controller.device is not None
    
    def test_tap_by_text(self, ui_controller):
        """Test tapping element by text."""
        mock_element = Mock()
        mock_element.exists = True
        ui_controller.device.return_value = mock_element
        
        result = ui_controller.tap(text="Send")
        
        assert result["success"] is True
        mock_element.click.assert_called_once()
    
    def test_tap_by_resource_id(self, ui_controller):
        """Test tapping element by resource ID."""
        mock_element = Mock()
        mock_element.exists = True
        ui_controller.device.return_value = mock_element
        
        result = ui_controller.tap(resource_id="com.app:id/button")
        
        assert result["success"] is True
    
    def test_tap_element_not_found(self, ui_controller):
        """Test tapping non-existent element."""
        mock_element = Mock()
        mock_element.exists = False
        ui_controller.device.return_value = mock_element
        
        result = ui_controller.tap(text="NonExistent")
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()
    
    def test_type_text(self, ui_controller):
        """Test typing text into element."""
        mock_element = Mock()
        mock_element.exists = True
        ui_controller.device.return_value = mock_element
        
        result = ui_controller.type_text("Hello World", text="Message")
        
        assert result["success"] is True
        mock_element.set_text.assert_called_once_with("Hello World")
    
    def test_type_text_no_selector(self, ui_controller):
        """Test typing text without selector (focused element)."""
        ui_controller.device.send_keys = Mock()
        
        result = ui_controller.type_text("Hello")
        
        assert result["success"] is True
        ui_controller.device.send_keys.assert_called_once_with("Hello")
    
    def test_find_element(self, ui_controller):
        """Test finding element."""
        mock_element = Mock()
        mock_element.exists = True
        mock_element.info = {"text": "Send", "clickable": True}
        ui_controller.device.return_value = mock_element
        
        result = ui_controller.find_element(text="Send")
        
        assert result["found"] is True
        assert result["element"]["text"] == "Send"
    
    def test_find_element_not_found(self, ui_controller):
        """Test finding non-existent element."""
        mock_element = Mock()
        mock_element.exists = False
        ui_controller.device.return_value = mock_element
        
        result = ui_controller.find_element(text="NonExistent")
        
        assert result["found"] is False
    
    def test_get_screen_structure(self, ui_controller):
        """Test getting screen structure."""
        ui_controller.device.dump_hierarchy = Mock(return_value="<xml>...</xml>")
        
        result = ui_controller.get_screen_structure()
        
        assert result is not None
        assert "elements" in result or "xml" in str(result).lower()
    
    def test_swipe(self, ui_controller):
        """Test swipe gesture."""
        ui_controller.device.swipe = Mock()
        
        result = ui_controller.swipe(100, 500, 100, 200)
        
        assert result["success"] is True
        ui_controller.device.swipe.assert_called_once()
    
    def test_navigate_back(self, ui_controller):
        """Test back navigation."""
        ui_controller.device.press = Mock()
        
        result = ui_controller.navigate_back()
        
        assert result["success"] is True
        ui_controller.device.press.assert_called_once_with("back")
    
    def test_navigate_home(self, ui_controller):
        """Test home navigation."""
        ui_controller.device.press = Mock()
        
        result = ui_controller.navigate_home()
        
        assert result["success"] is True
        ui_controller.device.press.assert_called_once_with("home")
