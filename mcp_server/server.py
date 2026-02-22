"""Main MCP Server implementation for Android ADB automation."""

import logging
import asyncio
import json
from typing import Any, Dict, Optional
from datetime import datetime

from mcp.server import Server
from mcp.types import Tool, TextContent

from mcp_server.config import Config
from mcp_server.device_manager import DeviceManager
from mcp_server.app_actions import AppActions
from mcp_server.utils.logging import setup_logging


logger = logging.getLogger("adb_mcp_server.mcp")


class AndroidADBMCPServer:
    """Main MCP server implementation for Android automation."""
    
    def __init__(self, config: Config):
        """
        Initialize MCP server.
        
        Args:
            config: Server configuration
        """
        self.config = config
        self.server = Server("android-adb-mcp")
        
        # Setup logging
        setup_logging(
            log_level=config.log_level,
            log_to_file=config.log_to_file,
            log_file_path=config.log_file_path
        )
        
        # Initialize device manager
        self.device_manager = DeviceManager(device_allowlist=config.device_allowlist)
        
        # Register tool handlers
        self._register_tools()
        
        logger.info("Android ADB MCP Server initialized")
    
    def _register_tools(self) -> None:
        """Register all MCP tools."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools."""
            return [
                Tool(
                    name="list_devices",
                    description="List all connected Android devices",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    }
                ),
                Tool(
                    name="select_device",
                    description="Set active device for subsequent operations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "device_id": {"type": "string", "description": "Device identifier"}
                        },
                        "required": ["device_id"]
                    }
                ),
                Tool(
                    name="open_app",
                    description="Open an application by name or package",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "app_name": {"type": "string", "description": "App name (e.g., 'instagram', 'whatsapp')"},
                            "package": {"type": "string", "description": "Package name (optional)"}
                        },
                        "required": ["app_name"]
                    }
                ),
                Tool(
                    name="send_message",
                    description="Send a message to a contact in specified app",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "app_name": {"type": "string", "description": "App name (instagram, whatsapp, telegram)"},
                            "contact_name": {"type": "string", "description": "Contact name"},
                            "message": {"type": "string", "description": "Message text"}
                        },
                        "required": ["app_name", "contact_name", "message"]
                    }
                ),
                Tool(
                    name="tap",
                    description="Tap an element by semantic identifier",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Element text"},
                            "content_desc": {"type": "string", "description": "Content description"},
                            "resource_id": {"type": "string", "description": "Resource ID"}
                        }
                    }
                ),
                Tool(
                    name="find_element",
                    description="Find UI elements matching criteria",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "content_desc": {"type": "string"},
                            "resource_id": {"type": "string"},
                            "class_name": {"type": "string"}
                        }
                    }
                ),
                Tool(
                    name="get_current_screen_structure",
                    description="Get structured representation of current screen",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_decorative": {"type": "boolean", "description": "Include decorative elements"}
                        }
                    }
                ),
                Tool(
                    name="type_text",
                    description="Type text into focused field or specified element",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Text to type"},
                            "element_text": {"type": "string", "description": "Element text to type into"},
                            "element_desc": {"type": "string", "description": "Element content-desc"}
                        },
                        "required": ["text"]
                    }
                ),
                Tool(
                    name="navigate_back",
                    description="Press Android back button",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="navigate_home",
                    description="Navigate to home screen",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="read_screen_text",
                    description="Extract all visible text from current screen",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="extract_otp",
                    description="Extract OTP code from SMS app",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="take_screenshot",
                    description="Capture current screen",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "output_path": {"type": "string", "description": "Output file path"}
                        }
                    }
                ),
                Tool(
                    name="install_app",
                    description="Install APK file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "apk_path": {"type": "string", "description": "Path to APK file"}
                        },
                        "required": ["apk_path"]
                    }
                ),
                Tool(
                    name="uninstall_app",
                    description="Uninstall application (requires confirmation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "package": {"type": "string", "description": "Package name"},
                            "confirm": {"type": "boolean", "description": "Confirmation flag"}
                        },
                        "required": ["package"]
                    }
                ),
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool calls."""
            start_time = datetime.now()
            
            try:
                result = await self.handle_tool_call(name, arguments)
                
                # Log tool call
                duration = (datetime.now() - start_time).total_seconds()
                from mcp_server.utils.logging import log_tool_call
                log_tool_call(name, arguments, result, duration)
                
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
            except Exception as e:
                logger.error(f"Tool call failed: {name} - {e}")
                error_result = {
                    "status": "error",
                    "error_type": type(e).__name__,
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                return [TextContent(type="text", text=json.dumps(error_result, indent=2))]
    
    async def handle_tool_call(self, tool_name: str, parameters: dict) -> dict:
        """
        Route tool calls to appropriate handlers.
        
        Args:
            tool_name: Name of tool to call
            parameters: Tool parameters
            
        Returns:
            Tool result dictionary
        """
        # Device management tools
        if tool_name == "list_devices":
            return await self._list_devices()
        elif tool_name == "select_device":
            return await self._select_device(parameters["device_id"])
        
        # Get active device controllers
        try:
            ui_controller = self.device_manager.get_ui_controller()
            adb_controller = self.device_manager.get_adb_controller()
            app_actions = AppActions(ui_controller, adb_controller)
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        
        # App control tools
        if tool_name == "open_app":
            return await self._open_app(app_actions, parameters)
        elif tool_name == "send_message":
            return await self._send_message(app_actions, parameters)
        
        # UI interaction tools
        elif tool_name == "tap":
            return await self._tap(ui_controller, parameters)
        elif tool_name == "find_element":
            return await self._find_element(ui_controller, parameters)
        elif tool_name == "get_current_screen_structure":
            return await self._get_screen_structure(ui_controller, parameters)
        elif tool_name == "type_text":
            return await self._type_text(ui_controller, adb_controller, parameters)
        elif tool_name == "navigate_back":
            return await self._navigate_back(adb_controller)
        elif tool_name == "navigate_home":
            return await self._navigate_home(adb_controller)
        elif tool_name == "read_screen_text":
            return await self._read_screen_text(ui_controller)
        
        # Workflow tools
        elif tool_name == "extract_otp":
            return await self._extract_otp(app_actions)
        
        # Utility tools
        elif tool_name == "take_screenshot":
            return await self._take_screenshot(adb_controller, parameters)
        elif tool_name == "install_app":
            return await self._install_app(adb_controller, parameters)
        elif tool_name == "uninstall_app":
            return await self._uninstall_app(adb_controller, parameters)
        
        else:
            return {"status": "error", "message": f"Unknown tool: {tool_name}"}
    
    # Tool implementation methods
    
    async def _list_devices(self) -> dict:
        """List all connected devices."""
        devices = self.device_manager.list_devices()
        return {
            "status": "success",
            "devices": devices,
            "count": len(devices)
        }
    
    async def _select_device(self, device_id: str) -> dict:
        """Select active device."""
        try:
            self.device_manager.set_active_device(device_id)
            return {"status": "success", "device": device_id}
        except ValueError as e:
            return {"status": "error", "message": str(e)}
    
    async def _open_app(self, app_actions: AppActions, params: dict) -> dict:
        """Open application."""
        result = app_actions.open_app_by_name(params["app_name"])
        return {
            "status": "success" if result.success else "error",
            "app": params["app_name"],
            "error": result.error
        }
    
    async def _send_message(self, app_actions: AppActions, params: dict) -> dict:
        """Send message via app."""
        app_name = params["app_name"].lower()
        contact = params["contact_name"]
        message = params["message"]
        
        if app_name == "instagram":
            result = app_actions.send_message_instagram(contact, message)
        elif app_name == "whatsapp":
            result = app_actions.send_message_whatsapp(contact, message)
        elif app_name == "telegram":
            result = app_actions.send_message_telegram(contact, message)
        else:
            return {"status": "error", "message": f"Unsupported app: {app_name}"}
        
        return {
            "status": "success" if result.success else "error",
            "contact": contact,
            "app": app_name,
            "completed_steps": result.completed_steps,
            "total_steps": result.total_steps,
            "error": result.error
        }
    
    async def _tap(self, ui_controller, params: dict) -> dict:
        """Tap element."""
        success = ui_controller.click_element(**params)
        return {
            "status": "success" if success else "error",
            "element": params
        }
    
    async def _find_element(self, ui_controller, params: dict) -> dict:
        """Find elements."""
        elements = ui_controller.find_elements(**params)
        return {
            "status": "success",
            "elements": [
                {
                    "text": e.text,
                    "content_desc": e.content_desc,
                    "resource_id": e.resource_id,
                    "bounds": e.bounds,
                    "clickable": e.clickable
                }
                for e in elements
            ],
            "count": len(elements)
        }
    
    async def _get_screen_structure(self, ui_controller, params: dict) -> dict:
        """Get screen structure."""
        include_decorative = params.get("include_decorative", False)
        structure = ui_controller.get_screen_structure(include_decorative)
        return {"status": "success", "screen": structure}
    
    async def _type_text(self, ui_controller, adb_controller, params: dict) -> dict:
        """Type text."""
        text = params["text"]
        
        if "element_text" in params or "element_desc" in params:
            criteria = {}
            if "element_text" in params:
                criteria["text"] = params["element_text"]
            if "element_desc" in params:
                criteria["content_desc"] = params["element_desc"]
            success = ui_controller.type_into_element(text, **criteria)
        else:
            success = adb_controller.input_text(text)
        
        return {"status": "success" if success else "error", "text": text}
    
    async def _navigate_back(self, adb_controller) -> dict:
        """Navigate back."""
        try:
            adb_controller.shell("input keyevent KEYCODE_BACK")
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _navigate_home(self, adb_controller) -> dict:
        """Navigate home."""
        try:
            adb_controller.shell("input keyevent KEYCODE_HOME")
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _read_screen_text(self, ui_controller) -> dict:
        """Read screen text."""
        hierarchy = ui_controller.get_ui_hierarchy()
        text_lines = [e.text for e in hierarchy.all_elements if e.text]
        return {"status": "success", "text": text_lines}
    
    async def _extract_otp(self, app_actions: AppActions) -> dict:
        """Extract OTP."""
        result = app_actions.extract_otp_from_sms()
        return {
            "status": "success" if result.success else "error",
            "otp": result.data.get("otp"),
            "error": result.error
        }
    
    async def _take_screenshot(self, adb_controller, params: dict) -> dict:
        """Take screenshot."""
        output_path = params.get("output_path", f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        try:
            path = adb_controller.take_screenshot(output_path)
            return {"status": "success", "image_path": path}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _install_app(self, adb_controller, params: dict) -> dict:
        """Install app."""
        success = adb_controller.install_apk(params["apk_path"])
        return {"status": "success" if success else "error"}
    
    async def _uninstall_app(self, adb_controller, params: dict) -> dict:
        """Uninstall app."""
        if self.config.require_confirmation_for_destructive and not params.get("confirm"):
            return {
                "status": "error",
                "message": "Confirmation required for destructive action. Set confirm=true"
            }
        
        success = adb_controller.uninstall_package(params["package"])
        return {"status": "success" if success else "error", "package": params["package"]}
    
    async def run(self):
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    """Main entry point."""
    import sys
    from pathlib import Path
    
    # Load configuration
    config_path = "config.yaml"
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    
    if Path(config_path).exists():
        config = Config.load_from_file(config_path)
    else:
        logger.warning(f"Config file not found: {config_path}, using defaults")
        config = Config()
    
    # Validate configuration
    errors = config.validate()
    if errors:
        logger.error(f"Configuration errors: {errors}")
        sys.exit(1)
    
    # Create and run server
    server = AndroidADBMCPServer(config)
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
