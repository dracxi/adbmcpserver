"""Logging utilities for Android ADB MCP Server."""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logging(
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_file_path: str = "adb_mcp_server.log"
) -> logging.Logger:
    """
    Configure logging system with console and file handlers.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to write logs to file
        log_file_path: Path to log file
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("adb_mcp_server")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_to_file:
        log_path = Path(log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def log_adb_command(
    device_id: Optional[str],
    command: str,
    duration: float,
    success: bool = True,
    error: Optional[str] = None
) -> None:
    """
    Log ADB command execution.
    
    Args:
        device_id: Device identifier (None for no device specified)
        command: ADB command executed
        duration: Execution time in seconds
        success: Whether command succeeded
        error: Error message if command failed
    """
    logger = logging.getLogger("adb_mcp_server.adb")
    
    device_str = f"[{device_id}]" if device_id else "[no device]"
    status = "SUCCESS" if success else "FAILED"
    
    log_msg = f"{device_str} {status} - Command: {command} - Duration: {duration:.3f}s"
    
    if success:
        logger.info(log_msg)
    else:
        logger.error(f"{log_msg} - Error: {error}")


def log_ui_interaction(
    action: str,
    element: dict,
    result: str,
    duration: Optional[float] = None
) -> None:
    """
    Log UI interaction.
    
    Args:
        action: Action performed (click, type, scroll, etc.)
        element: Element identifier dict (text, content_desc, resource_id, etc.)
        result: Result of interaction (success, error message, etc.)
        duration: Execution time in seconds
    """
    logger = logging.getLogger("adb_mcp_server.ui")
    
    # Format element identifier
    element_parts: list[str] = []
    if element.get('text'):
        element_parts.append(f"text='{element['text']}'")
    if element.get('content_desc'):
        element_parts.append(f"desc='{element['content_desc']}'")
    if element.get('resource_id'):
        element_parts.append(f"id='{element['resource_id']}'")
    if element.get('class_name'):
        element_parts.append(f"class='{element['class_name']}'")
    
    element_str = ", ".join(element_parts) if element_parts else "unknown"
    
    duration_str = f" - Duration: {duration:.3f}s" if duration is not None else ""
    log_msg = f"Action: {action} - Element: [{element_str}] - Result: {result}{duration_str}"
    
    if "success" in result.lower() or "found" in result.lower():
        logger.info(log_msg)
    elif "error" in result.lower() or "failed" in result.lower():
        logger.error(log_msg)
    else:
        logger.warning(log_msg)


def log_tool_call(
    tool_name: str,
    parameters: dict,
    response: dict,
    duration: float
) -> None:
    """
    Log MCP tool invocation.
    
    Args:
        tool_name: Name of the tool called
        parameters: Tool parameters
        response: Tool response
        duration: Execution time in seconds
    """
    logger = logging.getLogger("adb_mcp_server.mcp")
    
    # Sanitize parameters (remove sensitive data)
    safe_params = {k: v for k, v in parameters.items() if k not in ['pin', 'password']}
    
    status = response.get('status', 'unknown')
    log_msg = f"Tool: {tool_name} - Status: {status} - Duration: {duration:.3f}s - Params: {safe_params}"
    
    if status == "success":
        logger.info(log_msg)
    elif status == "error":
        error_type = response.get('error_type', 'Unknown')
        error_msg = response.get('message', 'No message')
        logger.error(f"{log_msg} - Error: {error_type}: {error_msg}")
    else:
        logger.warning(log_msg)


def log_workflow_step(
    workflow_name: str,
    step_number: int,
    total_steps: int,
    step_description: str,
    result: str
) -> None:
    """
    Log workflow step execution.
    
    Args:
        workflow_name: Name of the workflow
        step_number: Current step number
        total_steps: Total number of steps
        step_description: Description of the step
        result: Result of step execution
    """
    logger = logging.getLogger("adb_mcp_server.workflow")
    
    log_msg = f"Workflow: {workflow_name} - Step {step_number}/{total_steps}: {step_description} - {result}"
    
    if "success" in result.lower() or "completed" in result.lower():
        logger.info(log_msg)
    elif "error" in result.lower() or "failed" in result.lower():
        logger.error(log_msg)
    else:
        logger.debug(log_msg)
