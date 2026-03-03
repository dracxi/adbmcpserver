# Examples

This directory contains example scripts demonstrating how to use the Android ADB MCP Server.

## Available Examples

### 1. tool_calls.py
Basic examples of individual MCP tool invocations.

**Usage:**
```bash
python examples/tool_calls.py
```

**Demonstrates:**
- Listing connected devices
- Opening apps
- Tapping UI elements
- Typing text
- Taking screenshots

### 2. test_scenario.py
End-to-end test scenario showing a complete workflow.

**Usage:**
```bash
python examples/test_scenario.py
```

**Demonstrates:**
- Device connection
- App navigation
- Multi-step interactions
- Error handling

### 3. workflow_example.py
Examples of using the workflow system for predefined UI paths.

**Usage:**
```bash
python examples/workflow_example.py
```

**Demonstrates:**
- Executing predefined workflows
- Listing available workflows
- Parameter substitution
- Workflow error handling

### 4. test_mcp_server.py
Testing the MCP server directly.

**Usage:**
```bash
python examples/test_mcp_server.py
```

**Demonstrates:**
- MCP server initialization
- Tool registration
- Server communication

### 5. instagram_workflow_example.py
Instagram-specific workflow examples.

**Usage:**
```bash
python examples/instagram_workflow_example.py
```

**Demonstrates:**
- Sending Instagram DMs
- Checking notifications
- Instagram-specific workflows

### 6. test_instagram_notifications.py
Testing Instagram notification workflows.

**Usage:**
```bash
python examples/test_instagram_notifications.py
```

**Demonstrates:**
- Notification checking
- Workflow validation
- Error scenarios

## Prerequisites

Before running examples:

1. **Connect Android device:**
   ```bash
   adb devices
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Configure workflows:**
   Edit `app_workflows.yaml` to add your app-specific workflows.

## Creating Custom Examples

To create your own example:

1. Import required modules:
   ```python
   from mcp_server.device_manager import DeviceManager
   from mcp_server.ui_controller import UIController
   from mcp_server.workflow_engine import WorkflowEngine
   ```

2. Initialize components:
   ```python
   device_manager = DeviceManager()
   devices = device_manager.list_devices()
   device_manager.select_device(devices[0])
   
   ui_controller = UIController(device_id=devices[0])
   workflow_engine = WorkflowEngine()
   ```

3. Execute operations:
   ```python
   # Direct UI interaction
   ui_controller.tap(text="Button")
   
   # Or use workflows
   workflow_engine.execute_workflow(
       "whatsapp",
       "send_message",
       {"contact_name": "John", "message": "Hi!"},
       ui_controller
   )
   ```

## Troubleshooting

### Device Not Found
```bash
# Check ADB connection
adb devices

# Restart ADB
adb kill-server
adb start-server
```

### Import Errors
```bash
# Ensure package is installed
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Workflow Errors
- Check `app_workflows.yaml` syntax
- Verify app is installed on device
- Ensure UI elements exist (use `get_current_screen_structure`)

## Contributing

To add new examples:
1. Create a new Python file in this directory
2. Add clear comments and docstrings
3. Update this README with usage instructions
4. Test on multiple devices if possible
