"""ADB Controller for executing Android Debug Bridge commands."""

import subprocess
import shlex
import time
import logging
from dataclasses import dataclass
from typing import Optional
from pathlib import Path


logger = logging.getLogger("adb_mcp_server.adb")


@dataclass
class CommandResult:
    """Result of ADB command execution."""
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float


class ADBController:
    """Handles low-level ADB command execution via subprocess."""
    
    def __init__(self, device_id: Optional[str] = None, timeout: int = 30):
        """
        Initialize ADB controller.
        
        Args:
            device_id: Optional device identifier for device-specific commands
            timeout: Command execution timeout in seconds
        """
        self.device_id = device_id
        self.timeout = timeout
        self._verify_adb_installed()
    
    def _verify_adb_installed(self) -> None:
        """Verify ADB is installed and accessible."""
        try:
            result = subprocess.run(
                ["adb", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("ADB is not properly installed")
            logger.debug(f"ADB version: {result.stdout.strip()}")
        except FileNotFoundError:
            raise RuntimeError("ADB not found. Please install Android SDK Platform Tools")
        except subprocess.TimeoutExpired:
            raise RuntimeError("ADB command timed out during verification")
    
    def execute_command(self, command: list[str]) -> CommandResult:
        """
        Execute ADB command and return result.
        
        Args:
            command: Command parts as list (e.g., ["shell", "input", "tap", "100", "200"])
            
        Returns:
            CommandResult with execution details
        """
        # Build full command with device selector if specified
        full_command = ["adb"]
        if self.device_id:
            full_command.extend(["-s", self.device_id])
        full_command.extend(command)
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            execution_time = time.time() - start_time
            
            cmd_result = CommandResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                execution_time=execution_time
            )
            
            # Log command execution
            from mcp_server.utils.logging import log_adb_command
            log_adb_command(
                self.device_id,
                " ".join(command),
                execution_time,
                cmd_result.success,
                cmd_result.stderr if not cmd_result.success else None
            )
            
            return cmd_result
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            logger.error(f"ADB command timed out after {execution_time:.2f}s: {' '.join(command)}")
            return CommandResult(
                success=False,
                stdout="",
                stderr=f"Command timed out after {self.timeout}s",
                exit_code=-1,
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"ADB command failed: {e}")
            return CommandResult(
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                execution_time=execution_time
            )
    
    def shell(self, command: str) -> str:
        """
        Execute shell command on device.
        
        Args:
            command: Shell command to execute
            
        Returns:
            Command output
            
        Raises:
            RuntimeError: If command fails
        """
        result = self.execute_command(["shell", command])
        if not result.success:
            raise RuntimeError(f"Shell command failed: {result.stderr}")
        return result.stdout.strip()
    
    def install_apk(self, apk_path: str) -> bool:
        """
        Install APK file on device.
        
        Args:
            apk_path: Path to APK file
            
        Returns:
            True if installation succeeded
        """
        if not Path(apk_path).exists():
            logger.error(f"APK file not found: {apk_path}")
            return False
        
        result = self.execute_command(["install", "-r", apk_path])
        return result.success and "Success" in result.stdout
    
    def uninstall_package(self, package: str) -> bool:
        """
        Uninstall package from device.
        
        Args:
            package: Package name to uninstall
            
        Returns:
            True if uninstallation succeeded
        """
        result = self.execute_command(["uninstall", package])
        return result.success and "Success" in result.stdout
    
    def launch_app(self, package: str, activity: Optional[str] = None) -> bool:
            """
            Launch application by package name.

            Args:
                package: Package name
                activity: Optional activity name (uses default if not specified)

            Returns:
                True if launch succeeded
            """
            if activity:
                # Use am start with explicit activity
                component = f"{package}/{activity}"
                result = self.execute_command([
                    "shell", "am", "start", "-n", component
                ])
            else:
                # Use monkey to launch app with default launcher activity
                result = self.execute_command([
                    "shell", "monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1"
                ])
            return result.success
    
    def force_stop(self, package: str) -> bool:
        """
        Force stop an application.
        
        Args:
            package: Package name to stop
            
        Returns:
            True if stop succeeded
        """
        result = self.execute_command(["shell", "am", "force-stop", package])
        return result.success
    
    def input_tap(self, x: int, y: int) -> bool:
        """
        Simulate tap at coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if tap succeeded
        """
        result = self.execute_command(["shell", "input", "tap", str(x), str(y)])
        return result.success
    
    def input_swipe(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        duration: int = 300
    ) -> bool:
        """
        Simulate swipe gesture.
        
        Args:
            x1: Start X coordinate
            y1: Start Y coordinate
            x2: End X coordinate
            y2: End Y coordinate
            duration: Swipe duration in milliseconds
            
        Returns:
            True if swipe succeeded
        """
        result = self.execute_command([
            "shell", "input", "swipe",
            str(x1), str(y1), str(x2), str(y2), str(duration)
        ])
        return result.success
    
    def input_text(self, text: str) -> bool:
        """
        Input text (handles escaping).
        
        Args:
            text: Text to input
            
        Returns:
            True if input succeeded
        """
        # Escape text for shell
        escaped_text = text.replace(" ", "%s").replace("'", "\\'").replace('"', '\\"')
        
        result = self.execute_command(["shell", "input", "text", escaped_text])
        return result.success
    
    def take_screenshot(self, output_path: str) -> str:
        """
        Capture screenshot and save to path.
        
        Args:
            output_path: Local path to save screenshot
            
        Returns:
            Path to saved screenshot
            
        Raises:
            RuntimeError: If screenshot fails
        """
        # Take screenshot on device
        device_path = "/sdcard/screenshot.png"
        result = self.execute_command(["shell", "screencap", "-p", device_path])
        
        if not result.success:
            raise RuntimeError(f"Screenshot failed: {result.stderr}")
        
        # Pull screenshot to local path
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        pull_result = self.execute_command(["pull", device_path, str(output_file)])
        
        if not pull_result.success:
            raise RuntimeError(f"Failed to pull screenshot: {pull_result.stderr}")
        
        # Clean up device screenshot
        self.execute_command(["shell", "rm", device_path])
        
        return str(output_file)
    
    def start_screen_record(self, output_path: str) -> subprocess.Popen:
        """
        Start screen recording (returns process handle).
        
        Args:
            output_path: Device path for recording
            
        Returns:
            Process handle for recording
        """
        command = ["adb"]
        if self.device_id:
            command.extend(["-s", self.device_id])
        command.extend(["shell", "screenrecord", output_path])
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        logger.info(f"Started screen recording to {output_path}")
        return process
    
    def stop_screen_record(self, process: subprocess.Popen) -> str:
        """
        Stop screen recording and return file path.
        
        Args:
            process: Recording process handle
            
        Returns:
            Device path to recording
        """
        # Send interrupt to stop recording
        process.terminate()
        process.wait(timeout=5)
        
        logger.info("Stopped screen recording")
        return "/sdcard/recording.mp4"
    
    def push_file(self, local_path: str, device_path: str) -> bool:
        """
        Push file to device.
        
        Args:
            local_path: Local file path
            device_path: Device destination path
            
        Returns:
            True if push succeeded
        """
        if not Path(local_path).exists():
            logger.error(f"Local file not found: {local_path}")
            return False
        
        result = self.execute_command(["push", local_path, device_path])
        return result.success
    
    def pull_file(self, device_path: str, local_path: str) -> bool:
        """
        Pull file from device.
        
        Args:
            device_path: Device file path
            local_path: Local destination path
            
        Returns:
            True if pull succeeded
        """
        output_file = Path(local_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        result = self.execute_command(["pull", device_path, local_path])
        return result.success
    
    def get_clipboard(self) -> str:
        """
        Get clipboard content.
        
        Returns:
            Clipboard text
        """
        try:
            return self.shell("cmd clipboard get-text")
        except RuntimeError:
            return ""
    
    def set_clipboard(self, text: str) -> bool:
        """
        Set clipboard content.
        
        Args:
            text: Text to set in clipboard
            
        Returns:
            True if succeeded
        """
        escaped_text = shlex.quote(text)
        result = self.execute_command(["shell", "cmd", "clipboard", "put-text", escaped_text])
        return result.success
