# Android ADB MCP Server

A production-ready Model Context Protocol (MCP) server for intelligent Android device automation via ADB. Built with Python, featuring semantic UI interaction, cross-app workflows, and minimal token usage for LLM agents.

## Features

- **ADB Integration**: Full device control via Android Debug Bridge
- **UI Automation**: Semantic element interaction using uiautomator2 (no raw coordinates)
- **Multi-Device Support**: Manage multiple connected Android devices
- **Cross-App Workflows**: Pre-built workflows for Instagram, WhatsApp, Telegram
- **Workflow System**: Define exact UI paths without increasing context/tokens ⭐ NEW
- **Context-Efficient**: Minimal token usage with structured JSON responses
- **Security**: Device allowlist, PIN authentication, destructive action confirmation
- **Performance**: Element caching, decorative filtering, connection reuse
- **Production-Ready**: Type hints, comprehensive logging, clean architecture

## Installation

### Prerequisites

1. **Python 3.10+**
2. **ADB (Android Debug Bridge)**
   - Install via Android SDK Platform Tools
   - Or use package manager: `apt install adb` (Linux) or `brew install android-platform-tools` (macOS)
3. **Android Device or Emulator**
   - Enable USB debugging in Developer Options
   - Connect via USB or WiFi

### Install Package

```bash
# Clone repository
git clone <repository-url>
cd android-adb-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Install development dependencies (optional)
pip install -e ".[dev]"

# Install OCR support (optional)
pip install -e ".[ocr]"
```

### Verify ADB Connection

```bash
# Check ADB is installed
adb version

# List connected devices
adb devices

# Should show:
# List of devices attached
# <device_id>    device
```

## Quick Start

### 1. Run Setup Script

```bash
./setup.sh
source venv/bin/activate
```

### 2. Configure Server (Optional)

Copy and edit `config.example.yaml` to `config.yaml` for custom settings. Default configuration works out of the box.

### 3. Start Server

```bash
# Start with default config
python -m mcp_server.server

# Start with custom config
python -m mcp_server.server /path/to/config.yaml
```

### 4. Configure MCP Client

See `mcp_configs.json` for configuration examples for various MCP clients (Claude Desktop, Kiro, Cline, Cursor, etc.).

Standard configuration format:
```json
{
  "mcpServers": {
    "android-adb": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/path/to/android-adb-mcp-server",
      "env": {
        "PYTHONPATH": "/path/to/android-adb-mcp-server"
      }
    }
  }
}
```

### 5. Use MCP Tools

The server exposes the following tools via MCP protocol:

#### Device Management
- `list_devices()` - List all connected devices
- `select_device(device_id)` - Set active device

#### App Control
- `open_app(app_name, package=None)` - Launch application
- `navigate_back()` - Press back button
- `navigate_home()` - Go to home screen

#### UI Interaction
- `tap(text=None, content_desc=None, resource_id=None)` - Tap element
- `type_text(text, element_identifier=None)` - Type text
- `find_element(...)` - Locate UI elements
- `get_current_screen_structure()` - Get screen layout

#### Workflows
- `send_message(app_name, contact_name, message)` - Send message via app
- `execute_workflow(app_name, workflow_name, parameters)` - Execute predefined workflow ⭐ NEW
- `list_workflows()` - List all available workflows ⭐ NEW
- `extract_otp()` - Extract OTP from SMS
- `read_screen_text()` - Read all visible text

#### Utilities
- `take_screenshot()` - Capture screen
- `install_app(apk_path)` - Install APK
- `uninstall_app(package, confirm=False)` - Remove app
- `get_notifications()` - Retrieve notifications

## Architecture

### Layered Design
```
MCP Server Layer (server.py)
    ↓
App Actions Layer (app_actions.py) - High-level workflows
    ↓
Workflow Engine (workflow_engine.py) - Predefined UI paths ⭐ NEW
    ↓
UI Controller Layer (ui_controller.py) - Semantic interaction
    ↓
ADB Controller Layer (adb_controller.py) - Low-level commands
    ↓
Device Manager Layer (device_manager.py) - Multi-device routing
```

## Workflow System ⭐ NEW

The workflow system allows you to define exact UI paths for common tasks without increasing context or tokens. Perfect for repetitive actions like sending messages.

### Quick Example

Instead of the AI exploring the UI every time:
```python
# Old way: 10-15 tool calls, 30-60 seconds
get_screen_structure() → find_element() → tap() → ...
```

Use predefined workflows:
```python
# New way: 1 tool call, 5-10 seconds
execute_workflow("whatsapp", "send_message", {
    "contact_name": "John",
    "message": "Hi there!"
})
```

### Benefits

✅ **10x Faster**: Single tool call vs multiple exploration steps
✅ **Zero Context Overhead**: Workflows loaded on-demand, not in every prompt
✅ **Reliable**: Exact UI paths, no guessing or trial-and-error
✅ **Maintainable**: Update UI paths in one place
✅ **Scalable**: Add unlimited apps without bloating context

### Available Workflows

- **WhatsApp**: `send_message`
- **Instagram**: `send_dm`
- **Telegram**: `send_message`

### Adding Custom Workflows

Edit `app_workflows.yaml`:

```yaml
gmail:
  package: "com.google.android.gm"
  workflows:
    send_email:
      steps:
        - action: tap
          selector: {content_desc: "Compose"}
        - action: type_text
          selector: {text: "To"}
          input: "{recipient}"
        - action: type_text
          selector: {text: "Subject"}
          input: "{subject}"
        - action: type_text
          input: "{body}"
        - action: tap
          selector: {content_desc: "Send"}
```

See `WORKFLOW_GUIDE.md` for detailed documentation.



### Project Structure
```
mcp_server/
├── server.py           # MCP server with 15+ tools
├── adb_controller.py   # ADB command execution
├── ui_controller.py    # UI automation with uiautomator2
├── device_manager.py   # Multi-device management
├── app_actions.py      # Cross-app workflows
├── config.py           # Configuration management
└── utils/
    ├── logging.py      # Logging utilities
    └── text_processing.py  # Text utilities
```

## Development

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_server --cov-report=html

# Run unit tests only
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v -m integration

# Run specific test file
pytest tests/unit/test_adb_controller.py
```

### Code Quality

```bash
# Format code
black mcp_server/ tests/

# Sort imports
isort mcp_server/ tests/

# Lint code
flake8 mcp_server/ tests/

# Type check
mypy mcp_server/

# Run all checks
pre-commit run --all-files
```

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

## Examples

See `examples/` directory for:
- `tool_calls.py` - Example MCP tool invocations
- `test_scenario.py` - End-to-end test scenarios

### Example: Send WhatsApp Message
```python
{
  "tool": "send_message",
  "parameters": {
    "app_name": "whatsapp",
    "contact_name": "John Doe",
    "message": "Hello from MCP!"
  }
}
```

### Example: Extract OTP
```python
{
  "tool": "extract_otp",
  "parameters": {}
}
```

## Documentation

- **README.md** - This file (overview and quick start)
- **QUICKSTART.md** - Detailed quick start guide
- **WORKFLOW_GUIDE.md** - Workflow system documentation
- **TUTORIAL.md** - Step-by-step tutorials
- **QUICK_REFERENCE.md** - Quick reference guide
- **CONTRIBUTING.md** - Contribution guidelines
- **examples/README.md** - Example scripts documentation
- **config.example.yaml** - Configuration template
- **mcp_configs.json** - MCP client configuration examples

## Troubleshooting

### Server Not Starting
- Check Python version: `python --version` (must be 3.10+)
- Verify dependencies: `pip list | grep mcp`
- Check ADB: `adb devices`
- Review logs: `cat adb_mcp_server.log`

### Device Not Found
- Run: `adb devices`
- Enable USB debugging on device
- Try: `adb kill-server && adb start-server`

### Tools Not Appearing in MCP Client
- Restart MCP client application
- Verify PYTHONPATH is set correctly
- Test server manually: `python -m mcp_server.server`

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or pull request.
