# Design Document: ADB Shell Command Tool

## Overview

This design specifies the implementation of a generic ADB shell command execution tool for the Android ADB MCP server. The tool enables execution of arbitrary shell commands on connected Android devices through the Model Context Protocol (MCP), complementing the existing specialized tools for UI interactions and app automation.

The ADB shell command tool provides a low-level interface for device control, allowing AI agents and developers to execute any valid ADB shell command while maintaining consistency with the existing architecture. This tool is essential for operations not covered by specialized tools, such as system configuration, file operations, and advanced debugging.

### Key Design Goals

1. **Simplicity**: Provide a straightforward interface for executing arbitrary shell commands
2. **Consistency**: Follow existing code patterns and response formats used throughout the codebase
3. **Safety**: Respect timeout configurations and provide clear error handling
4. **Integration**: Seamlessly integrate with existing device management and ADB controller components
5. **Observability**: Comprehensive logging of command execution for debugging and auditing

### Scope

This design covers:
- Tool registration and schema definition in the MCP server
- Integration with DeviceManager for device selection
- Command execution through ADBController
- Response formatting and error handling
- Logging and observability

This design does NOT cover:
- Command validation or sandboxing (commands are executed as-is)
- Interactive shell sessions (only single command execution)
- Command history or caching mechanisms

## Architecture

### Component Overview

The ADB shell command tool integrates with three existing components:

```
┌─────────────────────────────────────────────────────────────┐
│                    AndroidADBMCPServer                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Tool Registration (_register_tools)                 │  │
│  │  - Defines "adb_shell" tool schema                   │  │
│  │  - Specifies input parameters and description        │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Tool Handler (handle_tool_call)                     │  │
│  │  - Routes "adb_shell" calls to _execute_shell        │  │
│  │  - Handles exceptions and formats responses          │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Shell Execution Handler (_execute_shell)           │  │
│  │  - Validates device selection                        │  │
│  │  - Retrieves ADBController from DeviceManager        │  │
│  │  - Executes command and formats response             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │       DeviceManager                  │
        │  - get_adb_controller()              │
        │  - Validates active device selection │
        └──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │       ADBController                  │
        │  - execute_command()                 │
        │  - Returns CommandResult             │
        └──────────────────────────────────────┘
```

### Integration Points

1. **MCP Server Registration**: The tool is registered in `AndroidADBMCPServer._register_tools()` alongside existing tools
2. **Tool Routing**: Calls are routed through `AndroidADBMCPServer.handle_tool_call()` to the new `_execute_shell()` handler
3. **Device Management**: Uses `DeviceManager.get_adb_controller()` to obtain the controller for the active device
4. **Command Execution**: Leverages `ADBController.execute_command()` for low-level ADB command execution
5. **Logging**: Uses existing `log_adb_command()` and `log_tool_call()` utilities for observability

### Data Flow

1. AI agent or client invokes the "adb_shell" tool via MCP with a command string
2. MCP server validates the request against the tool schema
3. `handle_tool_call()` routes the request to `_execute_shell()`
4. `_execute_shell()` validates device selection via DeviceManager
5. ADBController executes the shell command with timeout protection
6. CommandResult is formatted into a JSON response
7. Response is logged and returned to the caller

## Components and Interfaces

### Tool Schema Definition

The tool is registered with the following MCP schema:

```python
Tool(
    name="adb_shell",
    description=(
        "Execute arbitrary ADB shell command on the active Android device. "
        "Returns stdout, stderr, exit code, and execution time. "
        "Examples: 'pm list packages', 'getprop ro.build.version.release', "
        "'dumpsys battery', 'settings get secure android_id'"
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Shell command to execute (without 'adb shell' prefix)"
            }
        },
        "required": ["command"]
    }
)
```

### Handler Method Signature

```python
async def _execute_shell(self, adb_controller, params: dict) -> dict:
    """
    Execute ADB shell command on active device.
    
    Args:
        adb_controller: ADBController instance for the active device
        params: Dictionary containing 'command' key
        
    Returns:
        Dictionary with status, stdout, stderr, exit_code, and execution_time
        
    Raises:
        No exceptions raised - all errors returned in response dict
    """
```

### Response Format

Success response:
```json
{
    "status": "success",
    "stdout": "command output text",
    "stderr": "",
    "exit_code": 0,
    "execution_time": 0.234,
    "command": "pm list packages"
}
```

Error response (command failed):
```json
{
    "status": "error",
    "stdout": "",
    "stderr": "error message from command",
    "exit_code": 1,
    "execution_time": 0.123,
    "command": "invalid_command"
}
```

Error response (no device selected):
```json
{
    "status": "error",
    "message": "No device selected. Use select_device tool first.",
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

Error response (timeout):
```json
{
    "status": "error",
    "stdout": "",
    "stderr": "Command timed out after 30s",
    "exit_code": -1,
    "execution_time": 30.001,
    "command": "long_running_command"
}
```

### Integration with Existing Components

#### DeviceManager Integration

The tool uses `DeviceManager.get_adb_controller()` to retrieve the ADB controller for the active device. This method:
- Validates that a device is selected (raises ValueError if not)
- Handles multi-device scenarios automatically
- Performs lazy initialization of the ADB controller
- Returns a configured ADBController instance

#### ADBController Integration

The tool uses `ADBController.execute_command()` which:
- Accepts a list of command parts: `["shell", command_string]`
- Automatically adds device selector (`-s device_id`) if configured
- Enforces timeout limits (default 30 seconds, configurable)
- Returns a CommandResult dataclass with all execution details
- Handles subprocess exceptions and converts them to CommandResult

#### Logging Integration

The tool uses two existing logging functions:
- `log_adb_command()`: Called automatically by ADBController.execute_command()
- `log_tool_call()`: Called by the MCP server's call_tool handler

## Data Models

### Input Model

```python
{
    "command": str  # Required: Shell command to execute
}
```

Constraints:
- `command` must be a non-empty string
- `command` should NOT include the "adb shell" prefix (added automatically)
- `command` can contain spaces, quotes, and special characters (handled by ADB)

### Output Model (Success)

```python
{
    "status": "success",
    "stdout": str,           # Standard output from command
    "stderr": str,           # Standard error from command (may be empty)
    "exit_code": int,        # Command exit code (0 for success)
    "execution_time": float, # Execution time in seconds
    "command": str           # Echo of executed command
}
```

### Output Model (Error)

```python
{
    "status": "error",
    "stdout": str,           # Partial output if any
    "stderr": str,           # Error message
    "exit_code": int,        # Exit code (-1 for timeout/exception)
    "execution_time": float, # Time until failure
    "command": str           # Echo of attempted command
}
```

Or for device selection errors:

```python
{
    "status": "error",
    "message": str,          # Human-readable error message
    "timestamp": str         # ISO 8601 timestamp
}
```

### CommandResult Dataclass (from ADBController)

```python
@dataclass
class CommandResult:
    success: bool            # True if exit_code == 0
    stdout: str              # Standard output
    stderr: str              # Standard error
    exit_code: int           # Process exit code
    execution_time: float    # Execution duration in seconds
```

This dataclass is returned by `ADBController.execute_command()` and is transformed into the JSON response format.


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property Reflection

After analyzing all acceptance criteria, I identified several redundancies:

- Requirements 1.3, 1.4, 1.5, 1.6 all specify that response fields must be present. These can be combined into a single comprehensive property about response completeness.
- Requirements 1.2 and 2.3 both address command routing to the correct device - these are logically equivalent.
- Requirements 3.1 and 6.3 both specify error status for failed commands - these are the same property.
- Requirements 3.2, 3.3 overlap with 1.4, 1.5 since these fields should always be present regardless of success/failure.
- Requirements 3.4 and 4.3 both address timeout error responses - these are the same edge case.
- Requirements 2.1 and 3.5 both address the no device selected error - these are identical.
- Requirements 6.5 and 7.5 both address logging behavior - these are the same property.

After consolidation, the unique testable properties are:

### Property 1: Command Acceptance

For any valid shell command string, the tool SHALL accept it as input without rejection.

**Validates: Requirements 1.1**

### Property 2: Response Completeness

For any shell command execution (successful or failed), the response SHALL include all required fields: status, stdout, stderr, exit_code, execution_time, and command.

**Validates: Requirements 1.3, 1.4, 1.5, 1.6, 6.2**

### Property 3: Success Status Correctness

For any shell command that completes with exit code 0, the response status field SHALL be "success".

**Validates: Requirements 6.1**

### Property 4: Error Status Correctness

For any shell command that completes with a non-zero exit code, the response status field SHALL be "error".

**Validates: Requirements 3.1, 6.3**

### Property 5: Execution Time Non-Negativity

For any shell command execution, the execution_time field SHALL be a non-negative number representing seconds.

**Validates: Requirements 1.6**

### Property 6: Timeout Enforcement

For any shell command that exceeds the configured timeout duration, the command SHALL be terminated and SHALL NOT continue executing.

**Validates: Requirements 4.1, 4.2**

### Property 7: JSON Response Format

For any tool invocation, the response SHALL be valid JSON with proper indentation (2 spaces).

**Validates: Requirements 6.4**

### Property 8: Logging Completeness

For any shell command execution, at least one log entry SHALL be created recording the command, device, duration, and result.

**Validates: Requirements 6.5, 7.5**

### Property 9: Device Routing Consistency

For any shell command executed when a device is selected, the command SHALL execute on that specific device and not on any other connected device.

**Validates: Requirements 1.2, 2.3**

### Edge Cases

The following edge cases require explicit testing but are not universal properties:

**Edge Case 1: No Device Selected Error**
When no device is selected, the tool SHALL return an error response with a message indicating device selection is required.
**Validates: Requirements 2.1, 3.5**

**Edge Case 2: Timeout Error Response**
When a command times out, the tool SHALL return an error response with stderr containing "timed out" and exit_code of -1.
**Validates: Requirements 3.4, 4.3**

**Edge Case 3: Tool Registration**
The tool SHALL appear in the list_tools response with name "adb_shell" and a schema requiring a "command" parameter of type string.
**Validates: Requirements 5.1, 5.3, 5.4**

## Error Handling

### Error Categories

The tool handles three categories of errors:

1. **Pre-execution Errors**: Errors that occur before command execution
   - No device selected
   - Invalid device ID
   - Device disconnected

2. **Execution Errors**: Errors during command execution
   - Command not found
   - Permission denied
   - Invalid syntax
   - Non-zero exit codes

3. **Timeout Errors**: Commands that exceed the timeout limit
   - Long-running commands
   - Hung processes
   - Unresponsive device

### Error Response Strategy

All errors are returned as structured JSON responses, never as exceptions. This ensures consistent error handling for MCP clients.

**Pre-execution errors** return:
```json
{
    "status": "error",
    "message": "Human-readable error description",
    "timestamp": "ISO 8601 timestamp"
}
```

**Execution and timeout errors** return:
```json
{
    "status": "error",
    "stdout": "Partial output if any",
    "stderr": "Error message or timeout message",
    "exit_code": -1,
    "execution_time": 30.001,
    "command": "attempted command"
}
```

### Error Logging

All errors are logged with appropriate severity:
- Pre-execution errors: WARNING level (user action required)
- Execution errors: INFO level (command failed normally)
- Timeout errors: ERROR level (abnormal termination)

### Timeout Handling

The tool respects the timeout configuration from ADBController (default 30 seconds). When a timeout occurs:

1. The subprocess is terminated by ADBController
2. A CommandResult is returned with success=False
3. stderr contains "Command timed out after Xs"
4. exit_code is set to -1
5. execution_time reflects the actual time until termination

The timeout is enforced at the subprocess level using Python's `subprocess.run(timeout=...)`, ensuring reliable termination even for hung commands.

### Device Selection Validation

Before executing any command, the tool validates device selection:

1. Calls `DeviceManager.get_adb_controller()` which raises ValueError if no device is selected
2. Catches the ValueError and returns a structured error response
3. Logs the error at WARNING level
4. Returns immediately without attempting command execution

This validation ensures that multi-device scenarios are handled correctly and users receive clear guidance when device selection is required.

## Testing Strategy

### Dual Testing Approach

The implementation will be validated using both unit tests and property-based tests:

- **Unit tests**: Verify specific examples, edge cases, and error conditions
- **Property tests**: Verify universal properties across randomized inputs

Both testing approaches are complementary and necessary for comprehensive coverage. Unit tests catch concrete bugs and validate specific scenarios, while property tests verify general correctness across a wide range of inputs.

### Property-Based Testing

Property-based tests will use the **Hypothesis** library for Python, which is the standard PBT framework for Python projects.

**Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Each test will be tagged with a comment referencing the design property
- Tag format: `# Feature: adb-shell-command-tool, Property {number}: {property_text}`

**Test Coverage**:
Each correctness property (1-9) will have a corresponding property-based test:

1. **Property 1 Test**: Generate random valid command strings, verify acceptance
2. **Property 2 Test**: Generate random commands, verify all response fields present
3. **Property 3 Test**: Generate commands that succeed, verify status="success"
4. **Property 4 Test**: Generate commands that fail, verify status="error"
5. **Property 5 Test**: Generate random commands, verify execution_time >= 0
6. **Property 6 Test**: Generate long-running commands, verify timeout termination
7. **Property 7 Test**: Generate random commands, verify JSON response validity
8. **Property 8 Test**: Generate random commands, verify log entries created
9. **Property 9 Test**: Generate commands with device selection, verify correct device execution

**Example Property Test Structure**:
```python
from hypothesis import given, strategies as st
import json

@given(st.text(min_size=1))
def test_property_1_command_acceptance(command):
    """
    Feature: adb-shell-command-tool, Property 1: Command Acceptance
    For any valid shell command string, the tool SHALL accept it as input.
    """
    # Test implementation
    pass
```

### Unit Testing

Unit tests will focus on:

1. **Specific Examples**: Common commands like "pm list packages", "getprop", "dumpsys"
2. **Edge Cases**: 
   - No device selected error
   - Timeout error response
   - Tool registration verification
   - Empty stdout/stderr handling
   - Special characters in commands
3. **Integration Points**:
   - DeviceManager integration
   - ADBController integration
   - Logging integration
4. **Response Format Validation**:
   - JSON structure correctness
   - Field type validation
   - Status value validation

**Example Unit Test Structure**:
```python
async def test_no_device_selected_error():
    """Test that tool returns error when no device is selected."""
    server = AndroidADBMCPServer(config)
    server.device_manager.active_device = None
    
    result = await server.handle_tool_call("adb_shell", {"command": "echo test"})
    
    assert result["status"] == "error"
    assert "device" in result["message"].lower()
    assert "select" in result["message"].lower()
```

### Test Data Strategy

**For Property Tests**:
- Use Hypothesis strategies to generate diverse command strings
- Include ASCII and Unicode characters
- Generate commands with various lengths (1-1000 characters)
- Include commands with quotes, spaces, and special shell characters

**For Unit Tests**:
- Use real ADB commands that are safe and deterministic
- Mock ADBController for error condition testing
- Use test fixtures for device configuration
- Capture and verify log output

### Coverage Goals

- Line coverage: >90% for new code
- Branch coverage: >85% for error handling paths
- Property test iterations: 100+ per property
- Unit test count: 15-20 tests covering all edge cases

### Continuous Integration

Tests will be integrated into the CI pipeline:
- Run on every commit and pull request
- Fail the build if any test fails
- Generate coverage reports
- Run property tests with increased iterations (500+) on main branch

