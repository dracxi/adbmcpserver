#!/bin/bash
# Test runner script for Android ADB MCP Server

set -e

echo "================================"
echo "Android ADB MCP Server - Tests"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${YELLOW}Warning: Virtual environment not activated${NC}"
    echo "Activating virtual environment..."
    source venv/bin/activate || {
        echo -e "${RED}Failed to activate virtual environment${NC}"
        exit 1
    }
fi

# Parse arguments
TEST_TYPE="${1:-all}"
COVERAGE="${2:-no}"

run_unit_tests() {
    echo -e "${GREEN}Running unit tests...${NC}"
    if [ "$COVERAGE" = "coverage" ]; then
        pytest tests/unit/ -v --cov=mcp_server --cov-report=term --cov-report=html
    else
        pytest tests/unit/ -v
    fi
}

run_integration_tests() {
    echo -e "${GREEN}Running integration tests...${NC}"
    pytest tests/integration/ -v -m integration
}

run_all_tests() {
    echo -e "${GREEN}Running all tests...${NC}"
    if [ "$COVERAGE" = "coverage" ]; then
        pytest -v --cov=mcp_server --cov-report=term --cov-report=html
    else
        pytest -v
    fi
}

run_linters() {
    echo -e "${GREEN}Running linters...${NC}"
    echo "  - flake8"
    flake8 mcp_server/ tests/ || echo -e "${YELLOW}flake8 found issues${NC}"
    
    echo "  - black (check)"
    black --check mcp_server/ tests/ || echo -e "${YELLOW}black found formatting issues${NC}"
    
    echo "  - isort (check)"
    isort --check-only mcp_server/ tests/ || echo -e "${YELLOW}isort found import sorting issues${NC}"
    
    echo "  - mypy"
    mypy mcp_server/ --ignore-missing-imports || echo -e "${YELLOW}mypy found type issues${NC}"
}

# Main execution
case "$TEST_TYPE" in
    unit)
        run_unit_tests
        ;;
    integration)
        run_integration_tests
        ;;
    lint)
        run_linters
        ;;
    all)
        run_all_tests
        ;;
    *)
        echo "Usage: $0 {all|unit|integration|lint} [coverage]"
        echo ""
        echo "Examples:"
        echo "  $0 all           - Run all tests"
        echo "  $0 unit          - Run unit tests only"
        echo "  $0 integration   - Run integration tests only"
        echo "  $0 lint          - Run linters"
        echo "  $0 all coverage  - Run all tests with coverage"
        exit 1
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Tests completed successfully${NC}"
    
    if [ "$COVERAGE" = "coverage" ]; then
        echo ""
        echo "Coverage report generated in htmlcov/index.html"
    fi
else
    echo ""
    echo -e "${RED}✗ Tests failed${NC}"
    exit 1
fi
