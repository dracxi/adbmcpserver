#!/usr/bin/env python3
"""Quick test to verify MCP server is working."""

import sys
import asyncio
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server.config import Config
from mcp_server.device_manager import DeviceManager


async def test_server():
    """Test basic server functionality."""
    print("=== Testing Android ADB MCP Server ===\n")
    
    # Test 1: Load config
    print("1. Loading configuration...")
    try:
        config = Config.load_from_file("config.yaml")
        errors = config.validate()
        if errors:
            print(f"   ✗ Config errors: {errors}")
            return False
        print("   ✓ Configuration loaded and validated\n")
    except Exception as e:
        print(f"   ✗ Config error: {e}\n")
        return False
    
    # Test 2: Initialize device manager
    print("2. Initializing device manager...")
    try:
        device_manager = DeviceManager(device_allowlist=config.device_allowlist)
        print("   ✓ Device manager initialized\n")
    except Exception as e:
        print(f"   ✗ Device manager error: {e}\n")
        return False
    
    # Test 3: Discover devices
    print("3. Discovering devices...")
    try:
        devices = device_manager.discover_devices()
        print(f"   Found {len(devices)} device(s):")
        for device in devices:
            print(f"   - {device.device_id} ({device.status})")
        print()
        
        if not devices:
            print("   ⚠ No devices connected. Connect a device to test further.\n")
            return True
        
        print("   ✓ Device discovery successful\n")
    except Exception as e:
        print(f"   ✗ Device discovery error: {e}\n")
        return False
    
    # Test 4: Get ADB controller
    print("4. Testing ADB controller...")
    try:
        adb = device_manager.get_adb_controller()
        result = adb.shell("echo 'Hello from ADB'")
        print(f"   ADB response: {result}")
        print("   ✓ ADB controller working\n")
    except Exception as e:
        print(f"   ✗ ADB controller error: {e}\n")
        return False
    
    # Test 5: Get UI controller
    print("5. Testing UI controller...")
    try:
        ui = device_manager.get_ui_controller()
        hierarchy = ui.get_ui_hierarchy()
        print(f"   Found {len(hierarchy.all_elements)} UI elements")
        print(f"   Actionable elements: {len(hierarchy.actionable_elements)}")
        print("   ✓ UI controller working\n")
    except Exception as e:
        print(f"   ✗ UI controller error: {e}\n")
        print(f"   Note: This may fail if uiautomator2 is not installed on device")
        print(f"   Run: python -m uiautomator2 init\n")
        return False
    
    print("="*50)
    print("✓ All tests passed! MCP server is ready.")
    print("="*50)
    return True


if __name__ == "__main__":
    success = asyncio.run(test_server())
    sys.exit(0 if success else 1)
