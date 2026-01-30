import os
import sys
import subprocess
import re
import xml.etree.ElementTree as ET
from typing import List, Optional, Dict
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("ADB")

print(f"DEBUG: PATH={os.environ.get('PATH')}")
print(f"DEBUG: ADB version: {subprocess.run(['adb', '--version'], capture_output=True, text=True).stdout}")

def run_adb(args: List[str], device_serial: Optional[str] = None) -> str:
    """Run an ADB command and return the output."""
    cmd = ["adb"]
    if device_serial:
        cmd.extend(["-s", device_serial])
    cmd.extend(args)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"

def _parse_hierarchy(xml_data: str) -> List[Dict]:
    """Helper to parse the XML hierarchy into a list of element dictionaries."""
    try:
        root = ET.fromstring(xml_data)
    except Exception:
        return []

    elements = []
    for node in root.findall(".//node"):
        bounds_str = node.get("bounds", "")
        matches = re.findall(r"\[(\d+),(\d+)\]", bounds_str)
        center = None
        if len(matches) == 2:
            try:
                x1, y1 = map(int, matches[0])
                x2, y2 = map(int, matches[1])
                center = ((x1 + x2) // 2, (y1 + y2) // 2)
            except (ValueError, IndexError):
                pass

        elements.append({
            "text": node.get("text", "").strip(),
            "content-desc": node.get("content-desc", "").strip(),
            "resource-id": node.get("resource-id", "").strip(),
            "class": node.get("class", "").strip(),
            "package": node.get("package", "").strip(),
            "clickable": node.get("clickable") == "true",
            "bounds": bounds_str,
            "center": center
        })
    return elements

@mcp.tool()
def get_packages(device_serial: Optional[str] = None) -> str:
    """Retrieve a list of all installed packages."""
    output = run_adb(["shell", "pm", "list", "packages"], device_serial)
    if output.startswith("Error"): return output
    packages = [line.replace("package:", "").strip() for line in output.split("\n") if line.startswith("package:")]
    return "\n".join(packages)

@mcp.tool()
def execute_adb_shell_command(command: str, device_serial: Optional[str] = None) -> str:
    """Execute an arbitrary shell command."""
    if command.startswith("adb shell "):
        inner_cmd = command[10:]
    elif command.startswith("adb "):
        inner_cmd = command[4:]
    else:
        inner_cmd = command
    
    args = ["shell"] + inner_cmd.split()
    return run_adb(args, device_serial)

@mcp.tool()
def take_screenshot(filename: str = "screenshot.png", device_serial: Optional[str] = None) -> str:
    """Capture the current screen and save to a local file."""
    # First save to device, then pull
    remote_path = "/sdcard/mcp_screenshot.png"
    run_adb(["shell", "screencap", "-p", remote_path], device_serial)
    run_adb(["pull", remote_path, filename], device_serial)
    return f"Screenshot saved to: {os.path.abspath(filename)}"

@mcp.tool()
def get_uilayout(device_serial: Optional[str] = None) -> str:
    """Dump the current UI hierarchy and extract all meaningful elements."""
    xml_data = run_adb(["shell", "uiautomator", "dump", "/dev/tty"], device_serial)
    # Some devices don't support dump to tty, try file method
    if "UI hierchary dumped to:" not in xml_data and not xml_data.strip().startswith("<?xml"):
         run_adb(["shell", "uiautomator", "dump", "/sdcard/view.xml"], device_serial)
         xml_data = run_adb(["shell", "cat", "/sdcard/view.xml"], device_serial)
    
    # Clean up XML (sometimes there's extra text)
    match = re.search(r"<\?xml.*?>.*?</hierarchy>", xml_data, re.DOTALL)
    if match:
        xml_data = match.group(0)
    
    elements = _parse_hierarchy(xml_data)
    
    result = []
    for el in elements:
        if el["text"] or el["content-desc"] or el["resource-id"]:
            info = [f"Element (Clickable: {el['clickable']}):"]
            if el["text"]: info.append(f"  Text: '{el['text']}'")
            if el["content-desc"]: info.append(f"  Description: '{el['content-desc']}'")
            if el["resource-id"]: info.append(f"  Resource ID: '{el['resource-id']}'")
            info.append(f"  Bounds: {el['bounds']}")
            if el["center"]: info.append(f"  Center: {el['center']}")
            result.append("\n".join(info))
    
    if not result:
        return "No meaningful elements found."
    return "\n\n".join(result)

@mcp.tool()
def touch(x: int, y: int, device_serial: Optional[str] = None) -> str:
    """Simulate a finger tap at coordinates."""
    run_adb(["shell", "input", "tap", str(x), str(y)], device_serial)
    return f"Touch at ({x}, {y})"

@mcp.tool()
def swipe(x1: int, y1: int, x2: int, y2: int, duration_ms: int = 500, device_serial: Optional[str] = None) -> str:
    """Simulate a swipe gesture."""
    run_adb(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms)], device_serial)
    return f"Swipe from ({x1}, {y1}) to ({x2}, {y2})"

@mcp.tool()
def launch_app(package_name: str, activity: Optional[str] = None, device_serial: Optional[str] = None) -> str:
    """Launch an app or activity."""
    if activity:
        run_adb(["shell", "am", "start", "-n", f"{package_name}/{activity}"], device_serial)
    else:
        run_adb(["shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"], device_serial)
    return f"Launched {package_name}"

@mcp.tool()
def stop_app(package_name: str, device_serial: Optional[str] = None) -> str:
    """Force stop an app."""
    run_adb(["shell", "am", "force-stop", package_name], device_serial)
    return f"Stopped {package_name}"

@mcp.tool()
def input_text(text: str, device_serial: Optional[str] = None) -> str:
    """Type text into focused field."""
    escaped = text.replace(" ", "%s")
    run_adb(["shell", "input", "text", escaped], device_serial)
    return f"Typed: {text}"


if __name__ == "__main__":
    # Run as a standard stdio MCP server
    mcp.run()
