"""Example MCP tool calls for Android ADB MCP Server."""

import asyncio
import json


async def example_tool_calls():
    """Demonstrate various MCP tool calls."""
    
    print("=== Android ADB MCP Server - Example Tool Calls ===\n")
    
    # Example 1: List devices
    print("1. List connected devices:")
    print(json.dumps({
        "tool": "list_devices",
        "parameters": {}
    }, indent=2))
    print()
    
    # Example 2: Select device
    print("2. Select active device:")
    print(json.dumps({
        "tool": "select_device",
        "parameters": {
            "device_id": "emulator-5554"
        }
    }, indent=2))
    print()
    
    # Example 3: Open app
    print("3. Open Instagram:")
    print(json.dumps({
        "tool": "open_app",
        "parameters": {
            "app_name": "instagram"
        }
    }, indent=2))
    print()
    
    # Example 4: Send message
    print("4. Send WhatsApp message:")
    print(json.dumps({
        "tool": "send_message",
        "parameters": {
            "app_name": "whatsapp",
            "contact_name": "John Doe",
            "message": "Hello from MCP!"
        }
    }, indent=2))
    print()
    
    # Example 5: Get screen structure
    print("5. Get current screen structure:")
    print(json.dumps({
        "tool": "get_current_screen_structure",
        "parameters": {
            "include_decorative": False
        }
    }, indent=2))
    print()
    
    # Example 6: Find element
    print("6. Find element by text:")
    print(json.dumps({
        "tool": "find_element",
        "parameters": {
            "text": "Send"
        }
    }, indent=2))
    print()
    
    # Example 7: Tap element
    print("7. Tap element:")
    print(json.dumps({
        "tool": "tap",
        "parameters": {
            "text": "Send"
        }
    }, indent=2))
    print()
    
    # Example 8: Type text
    print("8. Type text:")
    print(json.dumps({
        "tool": "type_text",
        "parameters": {
            "text": "Hello World!"
        }
    }, indent=2))
    print()
    
    # Example 9: Extract OTP
    print("9. Extract OTP from SMS:")
    print(json.dumps({
        "tool": "extract_otp",
        "parameters": {}
    }, indent=2))
    print()
    
    # Example 10: Take screenshot
    print("10. Take screenshot:")
    print(json.dumps({
        "tool": "take_screenshot",
        "parameters": {
            "output_path": "screenshots/screen.png"
        }
    }, indent=2))
    print()
    
    # Example 11: Navigate back
    print("11. Navigate back:")
    print(json.dumps({
        "tool": "navigate_back",
        "parameters": {}
    }, indent=2))
    print()
    
    # Example 12: Read screen text
    print("12. Read all screen text:")
    print(json.dumps({
        "tool": "read_screen_text",
        "parameters": {}
    }, indent=2))
    print()


if __name__ == "__main__":
    asyncio.run(example_tool_calls())
