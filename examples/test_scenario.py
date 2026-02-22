"""End-to-end test scenario for Android ADB MCP Server."""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.config import Config
from mcp_server.device_manager import DeviceManager
from mcp_server.app_actions import AppActions


def test_basic_operations():
    """Test basic device operations."""
    print("=== Testing Basic Operations ===\n")
    
    # Initialize
    config = Config()
    device_manager = DeviceManager()
    
    # List devices
    print("1. Listing devices...")
    devices = device_manager.list_devices()
    print(f"   Found {len(devices)} device(s)")
    for device in devices:
        print(f"   - {device['device_id']} ({device['status']})")
    
    if not devices:
        print("   ERROR: No devices connected!")
        return False
    
    print("   ✓ Device listing successful\n")
    
    # Get controllers
    print("2. Initializing controllers...")
    try:
        adb_controller = device_manager.get_adb_controller()
        ui_controller = device_manager.get_ui_controller()
        print("   ✓ Controllers initialized\n")
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    # Test ADB command
    print("3. Testing ADB command...")
    try:
        result = adb_controller.shell("echo 'Hello ADB'")
        print(f"   Result: {result}")
        print("   ✓ ADB command successful\n")
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    # Test UI hierarchy
    print("4. Testing UI hierarchy retrieval...")
    try:
        hierarchy = ui_controller.get_ui_hierarchy()
        print(f"   Found {len(hierarchy.all_elements)} total elements")
        print(f"   Found {len(hierarchy.actionable_elements)} actionable elements")
        print("   ✓ UI hierarchy retrieval successful\n")
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    # Test screen structure
    print("5. Testing screen structure...")
    try:
        structure = ui_controller.get_screen_structure()
        print(f"   App: {structure['app_package']}")
        print(f"   Elements: {structure['total_elements']}")
        print("   ✓ Screen structure successful\n")
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    return True


def test_app_workflow():
    """Test app workflow operations."""
    print("=== Testing App Workflow ===\n")
    
    # Initialize
    device_manager = DeviceManager()
    
    try:
        adb_controller = device_manager.get_adb_controller()
        ui_controller = device_manager.get_ui_controller()
        app_actions = AppActions(ui_controller, adb_controller)
    except Exception as e:
        print(f"ERROR: Failed to initialize: {e}")
        return False
    
    # Test open app
    print("1. Testing open app...")
    try:
        result = app_actions.open_app_by_name("settings")
        if result.success:
            print("   ✓ App opened successfully")
            time.sleep(2)
        else:
            print(f"   WARNING: {result.error}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print()
    
    # Test navigation
    print("2. Testing navigation...")
    try:
        adb_controller.shell("input keyevent KEYCODE_HOME")
        print("   ✓ Navigated to home")
        time.sleep(1)
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print()
    
    return True


def main():
    """Run all test scenarios."""
    print("╔════════════════════════════════════════════════╗")
    print("║  Android ADB MCP Server - Test Scenario       ║")
    print("╚════════════════════════════════════════════════╝\n")
    
    # Check ADB
    print("Checking ADB installation...")
    import subprocess
    try:
        result = subprocess.run(["adb", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ ADB is installed\n")
        else:
            print("✗ ADB check failed\n")
            return
    except FileNotFoundError:
        print("✗ ADB not found. Please install Android SDK Platform Tools\n")
        return
    
    # Run tests
    success = True
    
    if not test_basic_operations():
        success = False
    
    if not test_app_workflow():
        success = False
    
    # Summary
    print("\n" + "="*50)
    if success:
        print("✓ All tests completed successfully!")
    else:
        print("✗ Some tests failed. Check output above.")
    print("="*50)


if __name__ == "__main__":
    main()
