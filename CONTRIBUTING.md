# Contributing to Android ADB MCP Server

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/yourusername/android-adb-mcp-server.git
cd android-adb-mcp-server
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v -m integration

# Run with coverage
pytest --cov=mcp_server --cov-report=html

# Run specific test file
pytest tests/unit/test_adb_controller.py -v
```

### Code Quality

```bash
# Format code with Black
black mcp_server/ tests/

# Sort imports with isort
isort mcp_server/ tests/

# Lint with flake8
flake8 mcp_server/ tests/

# Type check with mypy
mypy mcp_server/

# Run all checks (pre-commit)
pre-commit run --all-files
```

### Adding New Features

1. **Write tests first** (TDD approach recommended)
2. **Implement the feature**
3. **Update documentation**
4. **Run all tests and linters**
5. **Submit pull request**

### Adding New Workflows

1. **Test the workflow manually** on a real device
2. **Document UI elements** (resource IDs, text, content descriptions)
3. **Add to `app_workflows.yaml`**:
   ```yaml
   app_name:
     package: "com.example.app"
     workflows:
       workflow_name:
         description: "What this workflow does"
         steps:
           - action: tap
             selector: {resource_id: "com.example:id/button"}
   ```
4. **Add tests** in `tests/integration/test_workflows.py`
5. **Update documentation** in `WORKFLOW_GUIDE.md`

## Code Style Guidelines

### Python Style

- Follow PEP 8
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use docstrings for all public functions and classes

### Example:

```python
def execute_workflow(
    app_name: str,
    workflow_name: str,
    parameters: dict[str, str],
    timeout: int = 60
) -> dict[str, any]:
    """Execute a predefined workflow.
    
    Args:
        app_name: Name of the application
        workflow_name: Name of the workflow to execute
        parameters: Parameters to substitute in workflow
        timeout: Maximum execution time in seconds
        
    Returns:
        Dictionary with execution results
        
    Raises:
        ValueError: If workflow not found
        TimeoutError: If execution exceeds timeout
    """
    # Implementation
    pass
```

### Commit Messages

Follow conventional commits format:

```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `style`: Code style changes (formatting)
- `chore`: Maintenance tasks

Examples:
```
feat(workflows): add Gmail send email workflow

fix(adb): handle device disconnection gracefully

docs(readme): update installation instructions

test(ui): add tests for element finding
```

## Testing Guidelines

### Unit Tests

- Test individual functions and methods
- Mock external dependencies (ADB, uiautomator2)
- Fast execution (< 1 second per test)
- Located in `tests/unit/`

### Integration Tests

- Test complete workflows end-to-end
- May use mock devices or real devices
- Mark with `@pytest.mark.integration`
- Located in `tests/integration/`

### Test Coverage

- Aim for > 80% code coverage
- All new features must include tests
- Bug fixes should include regression tests

## Documentation

### Update Documentation When:

- Adding new features
- Changing existing behavior
- Adding new workflows
- Fixing bugs that affect usage

### Documentation Files:

- `README.md` - Project overview and quick start
- `QUICKSTART.md` - Detailed setup guide
- `WORKFLOW_GUIDE.md` - Workflow system documentation
- `TUTORIAL.md` - Step-by-step tutorials
- `QUICK_REFERENCE.md` - Quick reference guide
- `examples/README.md` - Example scripts documentation

## Pull Request Process

1. **Ensure all tests pass**
   ```bash
   pytest
   ```

2. **Ensure code quality checks pass**
   ```bash
   pre-commit run --all-files
   ```

3. **Update documentation** as needed

4. **Create pull request** with:
   - Clear title and description
   - Reference to related issues
   - Screenshots/videos for UI changes
   - Test results

5. **Respond to review feedback**

6. **Squash commits** if requested

## Project Structure

```
android-adb-mcp-server/
├── mcp_server/           # Main package
│   ├── server.py         # MCP server implementation
│   ├── adb_controller.py # ADB command execution
│   ├── ui_controller.py  # UI automation
│   ├── device_manager.py # Device management
│   ├── app_actions.py    # High-level app actions
│   ├── workflow_engine.py # Workflow execution
│   ├── config.py         # Configuration management
│   └── utils/            # Utility modules
├── tests/                # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── fixtures/         # Test fixtures
├── examples/             # Example scripts
├── docs/                 # Documentation
└── .github/              # GitHub workflows
```

## Getting Help

- **Issues**: Open an issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check existing documentation first

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
