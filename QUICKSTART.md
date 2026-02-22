# Quick Start Guide

## Prerequisites

1. **Python 3.10+** installed
2. **ADB (Android Debug Bridge)** installed
3. **Android device or emulator** with USB debugging enabled

## Installation

### 1. Install ADB

**Linux:**
```bash
sudo apt update
sudo apt install adb
```

**macOS:**
```bash
brew install android-platform-tools
```

**Windows:**
Download from [Android SDK Platform Tools](https://developer.android.com/studio/releases/platform-tools)

### 2. Setup Project

```bash
# Run setup script
chmod +x setup.sh
./setup.sh

# Or manual setup:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### 3. Connect Android Device

**Enable USB Debugging:**
1. Go to Settings → About Phone
2. Tap "Build Number" 7 times to enable Developer Options
3. Go to Settings → Developer Options
4. Enable "USB Debugging"
5. Connect device via USB

**Verify Connection:**
```bash
adb devices
# Should show:
# List of devices attached
# ABC123DEF456    device
```

## Usage

### Start the MCP Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start server
python -m mcp_server.server

# Or with custom config:
python -m mcp_server.server path/to/config.yaml
```

### Test the Server

```bash
# Run test scenario
python examples/test_scenario.py

# View example tool calls
python examples/tool_calls.py
```

## Example Tool Calls

### 1. List Devices
```json
{
  "tool": "list_devices",
  "parameters": {}
}
```

### 2. Open Instagram
```json
{
  "tool": "open_app",
  "parameters": {
    "app_name": "instagram"
  }
}
```

### 3. Send WhatsApp Message
```json
{
  "tool": "send_message",
  "parameters": {
    "app_name": "whatsapp",
    "contact_name": "John Doe",
    "message": "Hello from MCP!"
  }
}
```

### 4. Get Screen Structure
```json
{
  "tool": "get_current_screen_structure",
  "parameters": {
    "include_decorative": false
  }
}
```

### 5. Extract OTP from SMS
```json
{
  "tool": "extract_otp",
  "parameters": {}
}
```

## Configuration

Edit `config.yaml` to customize:

```yaml
# Timeouts
adb_command_timeout: 30
ui_wait_timeout: 10

# Security
device_allowlist: []  # Empty = allow all
require_pin: false

# Logging
log_level: "INFO"
log_to_file: true

# Performance
enable_element_caching: true
filter_decorative_elements: true
```

## Troubleshooting

### Device Not Found
```bash
# Check ADB connection
adb devices

# Restart ADB server
adb kill-server
adb start-server

# Check device authorization
# Look for authorization prompt on device
```

### uiautomator2 Connection Issues
```bash
# Install uiautomator2 on device
python -m uiautomator2 init

# Or manually:
adb install -r app-uiautomator.apk
adb install -r app-uiautomator-test.apk
```

### Permission Denied
```bash
# Check USB debugging is enabled
# Revoke and re-grant USB debugging authorization
# Try different USB cable or port
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [examples/](examples/) for more usage examples
- Review [config.example.yaml](config.example.yaml) for all configuration options
- See the spec documents in `~/.kiro/specs/android-adb-mcp-server/` for architecture details

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in `adb_mcp_server.log`
3. Run test scenario to verify setup: `python examples/test_scenario.py`
