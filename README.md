# ADB MCP Server

ADB MCP Server is a **Model Context Protocol (MCP)** server that exposes **Android Debug Bridge (ADB)** functionality as MCP tools.

It allows MCP-compatible AI clients to inspect Android UI layouts, simulate touch input, control apps, and execute shell commands.

---

## Files

```
adbmcpserver/
├── adbmcp.py        # MCP server implementation
└── mcp_config.json  # MCP client configuration
```

---

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install mcp
```

> Ensure `adb` is installed and available in your system PATH.

---

## Running the Server

```bash
python adbmcp.py
```

Runs as a **stdio-based MCP server**.

---

## MCP Configuration Example

```json
{
  "mcpServers": {
    "adbmcp": {
      "command": "python",
      "args": [
        "-u",
        "adbmcp.py"
      ]
    }
  }
}

```

Update paths according to your environment.

---

## Available MCP Tools

### Device & Shell
- `get_packages()`
- `execute_adb_shell_command(command)`
- `take_screenshot(filename)`

### UI Automation
- `get_uilayout()`
- `touch(x, y)`
- `swipe(x1, y1, x2, y2, duration_ms)`

### App Control
- `launch_app(package_name, activity=None)`
- `stop_app(package_name)`
- `input_text(text)`

---

## MCP Usage Example

```
1. get_uilayout()
2. Extract clickable element center
3. touch(x, y)
4. input_text("hello")
5. take_screenshot("screen.png")
```

---

## Notes

- USB debugging must be enabled
- Device must be authorized for ADB
- Some OEM ROMs restrict `uiautomator dump`
- Shell access is powerful and not sandboxed

---

## License

MIT
