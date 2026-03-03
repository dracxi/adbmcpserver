"""Mock device fixtures for testing."""
from unittest.mock import Mock


def create_mock_device(device_id="test_device", model="Pixel 6", android_version="12"):
    """Create a mock Android device for testing.
    
    Args:
        device_id: Device identifier
        model: Device model name
        android_version: Android OS version
        
    Returns:
        Mock device object with common methods
    """
    device = Mock()
    device.device_id = device_id
    device.info = {
        "productName": model,
        "version": android_version,
        "sdkInt": 31,
        "displayWidth": 1080,
        "displayHeight": 2400
    }
    
    # Mock common methods
    device.press = Mock(return_value=True)
    device.swipe = Mock(return_value=True)
    device.click = Mock(return_value=True)
    device.send_keys = Mock(return_value=True)
    device.dump_hierarchy = Mock(return_value="<xml></xml>")
    
    return device


def create_mock_element(text="", resource_id="", content_desc="", clickable=True, exists=True):
    """Create a mock UI element for testing.
    
    Args:
        text: Element text
        resource_id: Element resource ID
        content_desc: Element content description
        clickable: Whether element is clickable
        exists: Whether element exists
        
    Returns:
        Mock UI element object
    """
    element = Mock()
    element.exists = exists
    element.info = {
        "text": text,
        "resourceId": resource_id,
        "contentDescription": content_desc,
        "clickable": clickable,
        "bounds": {"left": 0, "top": 0, "right": 100, "bottom": 50}
    }
    
    element.click = Mock(return_value=True)
    element.set_text = Mock(return_value=True)
    element.get_text = Mock(return_value=text)
    element.wait = Mock(return_value=True)
    
    return element


def create_mock_adb_output(success=True, stdout="", stderr=""):
    """Create mock ADB command output.
    
    Args:
        success: Whether command succeeded
        stdout: Standard output
        stderr: Standard error
        
    Returns:
        Mock subprocess result
    """
    result = Mock()
    result.returncode = 0 if success else 1
    result.stdout = stdout
    result.stderr = stderr
    
    return result


# Common device configurations
MOCK_DEVICES = {
    "pixel_6": {
        "device_id": "ABC123DEF456",
        "model": "Pixel 6",
        "android_version": "12"
    },
    "samsung_s21": {
        "device_id": "XYZ789GHI012",
        "model": "Samsung Galaxy S21",
        "android_version": "11"
    },
    "emulator": {
        "device_id": "emulator-5554",
        "model": "Android Emulator",
        "android_version": "13"
    }
}


def get_mock_device_config(device_type="pixel_6"):
    """Get predefined mock device configuration.
    
    Args:
        device_type: Type of device (pixel_6, samsung_s21, emulator)
        
    Returns:
        Device configuration dict
    """
    return MOCK_DEVICES.get(device_type, MOCK_DEVICES["pixel_6"])
