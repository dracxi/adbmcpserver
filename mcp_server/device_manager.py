"""Device Manager for handling multiple Android devices."""

import logging
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict
from mcp_server.adb_controller import ADBController


logger = logging.getLogger("adb_mcp_server.device")


@dataclass
class DeviceInfo:
    """Information about a connected Android device."""
    device_id: str
    status: str  # "device", "offline", "unauthorized"
    model: Optional[str] = None
    android_version: Optional[str] = None
    adb_controller: Optional[ADBController] = None
    ui_controller: Optional[any] = None  # Will be UIController, avoiding circular import
    last_seen: datetime = None
    
    def __post_init__(self):
        if self.last_seen is None:
            self.last_seen = datetime.now()


class DeviceManager:
    """Manages multiple Android devices and routing."""
    
    def __init__(self, device_allowlist: list[str] = None):
        """
        Initialize device manager.
        
        Args:
            device_allowlist: List of allowed device IDs (empty = allow all)
        """
        self.devices: Dict[str, DeviceInfo] = {}
        self.active_device: Optional[str] = None
        self.allowlist: set[str] = set(device_allowlist or [])
        
        # Discover devices on initialization
        self.discover_devices()
    
    def discover_devices(self) -> list[DeviceInfo]:
        """
        Discover all connected devices using 'adb devices'.
        
        Returns:
            List of discovered devices
        """
        try:
            result = subprocess.run(
                ["adb", "devices", "-l"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to discover devices: {result.stderr}")
                return []
            
            devices = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                if not line.strip():
                    continue
                
                parts = line.split()
                if len(parts) < 2:
                    continue
                
                device_id = parts[0]
                status = parts[1]
                
                # Parse device info from additional fields
                model = None
                for part in parts[2:]:
                    if part.startswith("model:"):
                        model = part.split(":")[1]
                
                # Register or update device
                if device_id in self.devices:
                    self.devices[device_id].status = status
                    self.devices[device_id].last_seen = datetime.now()
                else:
                    device_info = DeviceInfo(
                        device_id=device_id,
                        status=status,
                        model=model
                    )
                    self.devices[device_id] = device_info
                
                devices.append(self.devices[device_id])
                
                # Set as active if it's the only device
                if len(self.devices) == 1 and self.active_device is None:
                    self.active_device = device_id
                    logger.info(f"Auto-selected device: {device_id}")
            
            logger.info(f"Discovered {len(devices)} device(s)")
            return devices
            
        except subprocess.TimeoutExpired:
            logger.error("Device discovery timed out")
            return []
        except Exception as e:
            logger.error(f"Device discovery failed: {e}")
            return []
    
    def register_device(self, device_id: str) -> DeviceInfo:
        """
        Register a device manually.
        
        Args:
            device_id: Device identifier
            
        Returns:
            DeviceInfo for the registered device
        """
        if device_id not in self.devices:
            device_info = DeviceInfo(
                device_id=device_id,
                status="device"
            )
            self.devices[device_id] = device_info
            logger.info(f"Registered device: {device_id}")
        
        return self.devices[device_id]
    
    def unregister_device(self, device_id: str) -> None:
        """
        Remove device from registry.
        
        Args:
            device_id: Device identifier to remove
        """
        if device_id in self.devices:
            del self.devices[device_id]
            logger.info(f"Unregistered device: {device_id}")
            
            # Clear active device if it was removed
            if self.active_device == device_id:
                self.active_device = None
                # Auto-select another device if available
                if self.devices:
                    self.active_device = next(iter(self.devices.keys()))
                    logger.info(f"Auto-selected new active device: {self.active_device}")
    
    def get_device(self, device_id: Optional[str] = None) -> DeviceInfo:
        """
        Get device info (uses active device if not specified).
        
        Args:
            device_id: Optional device identifier
            
        Returns:
            DeviceInfo for the specified or active device
            
        Raises:
            ValueError: If device not found or no device selected
        """
        # Use active device if not specified
        if device_id is None:
            device_id = self.active_device
        
        if device_id is None:
            if len(self.devices) == 0:
                raise ValueError("No devices connected")
            elif len(self.devices) > 1:
                raise ValueError(
                    f"Multiple devices connected ({len(self.devices)}). "
                    "Please select a device using select_device()"
                )
            else:
                # Only one device, use it
                device_id = next(iter(self.devices.keys()))
                self.active_device = device_id
        
        if device_id not in self.devices:
            raise ValueError(f"Device not found: {device_id}")
        
        return self.devices[device_id]
    
    def set_active_device(self, device_id: str) -> None:
        """
        Set the active device for subsequent operations.
        
        Args:
            device_id: Device identifier to set as active
            
        Raises:
            ValueError: If device not found or not allowed
        """
        if device_id not in self.devices:
            raise ValueError(f"Device not found: {device_id}")
        
        if not self.is_device_allowed(device_id):
            raise ValueError(f"Device not in allowlist: {device_id}")
        
        self.active_device = device_id
        logger.info(f"Set active device: {device_id}")
    
    def is_device_allowed(self, device_id: str) -> bool:
        """
        Check if device is in allowlist.
        
        Args:
            device_id: Device identifier to check
            
        Returns:
            True if device is allowed (or allowlist is empty)
        """
        # Empty allowlist means all devices allowed
        if not self.allowlist:
            return True
        
        return device_id in self.allowlist
    
    def get_adb_controller(
        self,
        device_id: Optional[str] = None,
        timeout: int = 30
    ) -> ADBController:
        """
        Get ADB controller for device (lazy initialization).
        
        Args:
            device_id: Optional device identifier
            timeout: Command timeout in seconds
            
        Returns:
            ADBController instance for the device
        """
        device_info = self.get_device(device_id)
        
        # Lazy initialize ADB controller
        if device_info.adb_controller is None:
            device_info.adb_controller = ADBController(
                device_id=device_info.device_id,
                timeout=timeout
            )
        
        return device_info.adb_controller
    
    def get_ui_controller(self, device_id: Optional[str] = None):
        """
        Get UI controller for device (lazy initialization).
        
        Args:
            device_id: Optional device identifier
            
        Returns:
            UIController instance for the device
        """
        device_info = self.get_device(device_id)
        
        # Lazy initialize UI controller
        if device_info.ui_controller is None:
            # Import here to avoid circular dependency
            from mcp_server.ui_controller import UIController
            
            adb_controller = self.get_adb_controller(device_id)
            device_info.ui_controller = UIController(
                device_id=device_info.device_id,
                adb_controller=adb_controller
            )
        
        return device_info.ui_controller
    
    def list_devices(self) -> list[dict]:
        """
        List all devices with their info.
        
        Returns:
            List of device info dictionaries
        """
        return [
            {
                "device_id": info.device_id,
                "status": info.status,
                "model": info.model,
                "android_version": info.android_version,
                "is_active": info.device_id == self.active_device,
                "is_allowed": self.is_device_allowed(info.device_id)
            }
            for info in self.devices.values()
        ]
