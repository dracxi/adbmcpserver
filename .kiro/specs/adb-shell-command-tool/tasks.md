# Implementation Plan: ADB Shell Command Tool

## Overview

This plan implements a generic ADB shell command execution tool for the Android ADB MCP server. The implementation adds a new "adb_shell" tool that enables execution of arbitrary shell commands on connected Android devices through the MCP protocol. The tool integrates with existing DeviceManager and ADBController components, follows established code patterns, and includes comprehensive testing with both property-based and unit tests.

## Tasks

- [x] 1. Add adb_shell tool registration to MCP server
  - Add Tool definition in `_register_tools()` method with name "adb_shell"
  - Define input schema requiring "command" parameter (type: string)
  - Include description with usage examples (pm list packages, getprop, dumpsys battery, settings get)
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 2. Implement shell command execution handler
  - [x] 2.1 Create `_execute_shell()` async method in AndroidADBMCPServer class
    - Accept adb_controller and params dict as parameters
    - Extract command string from params["command"]
    - Call adb_controller.execute_command(["shell", command])
    - Format CommandResult into JSON response with all required fields
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_
  
  - [ ]* 2.2 Write property test for response completeness
    - **Property 2: Response Completeness**
    - **Validates: Requirements 1.3, 1.4, 1.5, 1.6, 6.2**
  
  - [ ]* 2.3 Write property test for execution time non-negativity
    - **Property 5: Execution Time Non-Negativity**
    - **Validates: Requirements 1.6**

- [x] 3. Add tool routing in handle_tool_call method
  - Add elif branch for tool_name == "adb_shell"
  - Route to `_execute_shell(adb_controller, parameters)`
  - Ensure routing occurs after device controller retrieval
  - _Requirements: 7.2_

- [x] 4. Implement response formatting logic
  - [x] 4.1 Format success responses with status="success"
    - Include stdout, stderr, exit_code, execution_time, command fields
    - Return dict matching success response schema
    - _Requirements: 6.1, 6.2_
  
  - [x] 4.2 Format error responses with status="error"
    - Include stdout, stderr, exit_code, execution_time, command fields for command failures
    - Include message and timestamp fields for pre-execution errors
    - Return dict matching error response schema
    - _Requirements: 3.1, 3.2, 3.3, 6.3_
  
  - [ ]* 4.3 Write property test for success status correctness
    - **Property 3: Success Status Correctness**
    - **Validates: Requirements 6.1**
  
  - [ ]* 4.4 Write property test for error status correctness
    - **Property 4: Error Status Correctness**
    - **Validates: Requirements 3.1, 6.3**
  
  - [ ]* 4.5 Write property test for JSON response format
    - **Property 7: JSON Response Format**
    - **Validates: Requirements 6.4**

- [x] 5. Implement device selection validation
  - [x] 5.1 Handle ValueError from get_adb_controller() when no device selected
    - Catch ValueError exception in _execute_shell
    - Return error response with message "No device selected. Use select_device tool first."
    - Include timestamp in ISO 8601 format
    - _Requirements: 2.1, 3.5_
  
  - [ ]* 5.2 Write unit test for no device selected error
    - Test that error response is returned when device_manager.active_device is None
    - Verify error message contains "device" and "select"
    - _Requirements: 2.1, 3.5_
  
  - [ ]* 5.3 Write property test for device routing consistency
    - **Property 9: Device Routing Consistency**
    - **Validates: Requirements 1.2, 2.3**

- [x] 6. Checkpoint - Ensure all tests pass
  - Run all unit tests and property tests
  - Verify tool appears in list_tools response
  - Test basic command execution manually if needed
  - Ask the user if questions arise

- [x] 7. Implement timeout handling
  - [x] 7.1 Verify ADBController timeout configuration is respected
    - Review ADBController.execute_command() implementation
    - Confirm timeout parameter is passed to subprocess.run()
    - Document timeout behavior in code comments
    - _Requirements: 4.1, 4.2_
  
  - [x] 7.2 Handle timeout errors in response formatting
    - Check for timeout indicators in CommandResult (exit_code=-1, stderr contains "timed out")
    - Format timeout errors with appropriate error response
    - _Requirements: 3.4, 4.3_
  
  - [ ]* 7.3 Write unit test for timeout error response
    - Mock ADBController to return timeout CommandResult
    - Verify error response contains "timed out" in stderr
    - Verify exit_code is -1
    - _Requirements: 3.4, 4.3_
  
  - [ ]* 7.4 Write property test for timeout enforcement
    - **Property 6: Timeout Enforcement**
    - **Validates: Requirements 4.1, 4.2**

- [x] 8. Add logging integration
  - [x] 8.1 Verify automatic logging by ADBController.execute_command()
    - Review existing log_adb_command() calls in ADBController
    - Confirm command, device, duration, and result are logged
    - _Requirements: 6.5, 7.5_
  
  - [x] 8.2 Verify tool call logging by MCP server call_tool handler
    - Review existing log_tool_call() in call_tool decorator
    - Confirm tool name, arguments, result, and duration are logged
    - _Requirements: 6.5, 7.5_
  
  - [ ]* 8.3 Write property test for logging completeness
    - **Property 8: Logging Completeness**
    - **Validates: Requirements 6.5, 7.5**

- [x] 9. Write unit tests for specific command examples
  - [ ]* 9.1 Write unit test for "pm list packages" command
    - Test successful execution with package list in stdout
    - Verify status="success" and exit_code=0
    - _Requirements: 1.1, 1.2, 6.1_
  
  - [ ]* 9.2 Write unit test for "getprop" command
    - Test successful execution with system properties in stdout
    - Verify all response fields are present
    - _Requirements: 1.1, 1.3, 1.4, 1.5, 1.6_
  
  - [ ]* 9.3 Write unit test for invalid command
    - Test command that doesn't exist (e.g., "nonexistent_command")
    - Verify status="error" and non-zero exit_code
    - Verify stderr contains error message
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [ ]* 9.4 Write unit test for command with special characters
    - Test command with quotes, spaces, and shell metacharacters
    - Verify command is executed correctly without shell injection
    - _Requirements: 1.1_

- [x] 10. Write unit test for tool registration
  - [ ]* 10.1 Verify tool appears in list_tools response
    - Call list_tools() and verify "adb_shell" is in returned tools
    - Verify tool has correct name, description, and input schema
    - Verify schema requires "command" parameter of type string
    - _Requirements: 5.1, 5.3, 5.4_

- [x] 11. Write property-based tests with Hypothesis
  - [ ]* 11.1 Write property test for command acceptance
    - **Property 1: Command Acceptance**
    - Generate random valid command strings using Hypothesis
    - Verify tool accepts all generated commands without rejection
    - Use st.text(min_size=1) strategy for command generation
    - Run minimum 100 iterations
    - _Requirements: 1.1**
  
  - [ ]* 11.2 Configure Hypothesis settings for all property tests
    - Set min_success_examples=100 for all property tests
    - Add property tags as comments in format: "# Feature: adb-shell-command-tool, Property N: {title}"
    - Document Hypothesis version requirement in test file
    - _Requirements: All property-based test requirements_

- [x] 12. Final checkpoint - Ensure all tests pass and integration is complete
  - Run full test suite (unit tests + property tests)
  - Verify code coverage meets >90% line coverage goal
  - Test integration with existing tools (list_devices, select_device, adb_shell)
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests use Hypothesis framework with minimum 100 iterations
- The tool leverages existing ADBController.execute_command() method - no changes needed to ADBController
- Response formatting follows existing patterns used by other tools in server.py
- Logging is handled automatically by existing infrastructure - no additional logging code needed
- All code follows async/await patterns established in the codebase
