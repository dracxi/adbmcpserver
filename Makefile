.PHONY: help install install-dev test test-unit test-integration coverage lint format clean

help:
	@echo "Available commands:"
	@echo "  make install          - Install package"
	@echo "  make install-dev      - Install package with dev dependencies"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make coverage         - Run tests with coverage report"
	@echo "  make lint             - Run all linters"
	@echo "  make format           - Format code with black and isort"
	@echo "  make clean            - Clean build artifacts"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest -v

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v -m integration

coverage:
	pytest --cov=mcp_server --cov-report=html --cov-report=term

lint:
	flake8 mcp_server/ tests/
	mypy mcp_server/
	black --check mcp_server/ tests/
	isort --check-only mcp_server/ tests/

format:
	black mcp_server/ tests/
	isort mcp_server/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
