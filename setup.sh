#!/bin/bash
# Setup script for Android ADB MCP Server

echo "=== Android ADB MCP Server Setup ==="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check ADB
echo ""
echo "Checking ADB installation..."
if command -v adb &> /dev/null; then
    adb_version=$(adb version 2>&1 | head -n 1)
    echo "✓ ADB found: $adb_version"
else
    echo "✗ ADB not found!"
    echo "Please install Android SDK Platform Tools:"
    echo "  - Linux: sudo apt install adb"
    echo "  - macOS: brew install android-platform-tools"
    echo "  - Or download from: https://developer.android.com/studio/releases/platform-tools"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -e .

# Create config file if it doesn't exist
if [ ! -f config.yaml ]; then
    echo ""
    echo "Creating default config.yaml..."
    cp config.example.yaml config.yaml
    echo "✓ Config file created"
fi

# Create directories
echo ""
echo "Creating directories..."
mkdir -p screenshots recordings logs

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Connect your Android device via USB"
echo "2. Enable USB debugging on your device"
echo "3. Run: adb devices (to verify connection)"
echo "4. Activate venv: source venv/bin/activate"
echo "5. Start server: python -m mcp_server.server"
echo ""
echo "For testing, run: python examples/test_scenario.py"
