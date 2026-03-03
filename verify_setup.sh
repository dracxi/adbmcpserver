#!/bin/bash
# Verification script for project setup

echo "================================"
echo "Project Setup Verification"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1 (missing)"
        ((ERRORS++))
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
    else
        echo -e "${RED}✗${NC} $1/ (missing)"
        ((ERRORS++))
    fi
}

check_executable() {
    if [ -x "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 (executable)"
    else
        echo -e "${YELLOW}⚠${NC} $1 (not executable)"
        ((WARNINGS++))
    fi
}

echo "Checking core files..."
check_file "README.md"
check_file "pyproject.toml"
check_file "requirements.txt"
check_file "setup.sh"
check_file "LICENSE"
check_file ".gitignore"
echo ""

echo "Checking configuration files..."
check_file "config.example.yaml"
check_file "mcp_configs.json"
check_file "app_workflows.yaml"
echo ""

echo "Checking documentation..."
check_file "QUICKSTART.md"
check_file "WORKFLOW_GUIDE.md"
check_file "TUTORIAL.md"
check_file "QUICK_REFERENCE.md"
check_file "CONTRIBUTING.md"
check_file "PROJECT_STATUS.md"
check_file "IMPROVEMENTS_SUMMARY.md"
echo ""

echo "Checking source code..."
check_dir "mcp_server"
check_file "mcp_server/__init__.py"
check_file "mcp_server/server.py"
check_file "mcp_server/adb_controller.py"
check_file "mcp_server/ui_controller.py"
check_file "mcp_server/device_manager.py"
check_file "mcp_server/app_actions.py"
check_file "mcp_server/workflow_engine.py"
check_file "mcp_server/config.py"
echo ""

echo "Checking test infrastructure..."
check_dir "tests"
check_dir "tests/unit"
check_dir "tests/integration"
check_dir "tests/fixtures"
check_file "tests/conftest.py"
check_file "tests/unit/test_adb_controller.py"
check_file "tests/unit/test_ui_controller.py"
check_file "tests/unit/test_device_manager.py"
check_file "tests/unit/test_workflow_engine.py"
check_file "tests/integration/test_workflows.py"
check_file "tests/fixtures/mock_devices.py"
check_file "tests/fixtures/sample_workflows.yaml"
echo ""

echo "Checking CI/CD..."
check_dir ".github/workflows"
check_file ".github/workflows/test.yml"
check_file ".github/workflows/lint.yml"
echo ""

echo "Checking development tools..."
check_file ".pre-commit-config.yaml"
check_file "Makefile"
check_file "run_tests.sh"
check_executable "run_tests.sh"
check_executable "setup.sh"
echo ""

echo "Checking examples..."
check_dir "examples"
check_file "examples/README.md"
check_file "examples/tool_calls.py"
check_file "examples/test_scenario.py"
check_file "examples/workflow_example.py"
echo ""

echo "================================"
echo "Summary"
echo "================================"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Install dependencies: make install-dev"
    echo "  2. Run tests: make test"
    echo "  3. Run linters: make lint"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ ${WARNINGS} warning(s)${NC}"
    echo ""
    echo "Fix warnings with:"
    echo "  chmod +x run_tests.sh setup.sh"
    exit 0
else
    echo -e "${RED}✗ ${ERRORS} error(s), ${WARNINGS} warning(s)${NC}"
    echo ""
    echo "Some files are missing. Please check the setup."
    exit 1
fi
