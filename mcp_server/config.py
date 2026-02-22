"""Configuration management for Android ADB MCP Server."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import yaml
import json


@dataclass
class Config:
    """System configuration for Android ADB MCP Server."""
    
    # Timeouts (seconds)
    adb_command_timeout: int = 30
    ui_wait_timeout: int = 10
    workflow_step_timeout: int = 15
    
    # Retries
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Security
    device_allowlist: list[str] = field(default_factory=list)
    require_pin: bool = False
    pin_hash: Optional[str] = None
    require_confirmation_for_destructive: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_to_file: bool = True
    log_file_path: str = "adb_mcp_server.log"
    
    # Performance
    enable_element_caching: bool = True
    cache_ttl_seconds: int = 5
    filter_decorative_elements: bool = True
    
    # Optional Features
    enable_ocr_fallback: bool = False
    enable_workflow_state_cache: bool = False
    
    @classmethod
    def load_from_file(cls, path: str) -> "Config":
        """
        Load configuration from YAML or JSON file.
        
        Args:
            path: Path to configuration file
            
        Returns:
            Config instance with loaded settings
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file format is invalid
        """
        config_path = Path(path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        try:
            with open(config_path, 'r') as f:
                if config_path.suffix in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                elif config_path.suffix == '.json':
                    data = json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")
            
            if data is None:
                data = {}
            
            # Create config with loaded data
            return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
        except TypeError as e:
            raise ValueError(f"Invalid configuration values: {e}")
    
    def validate(self) -> list[str]:
        """
        Validate configuration and return list of errors.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Validate timeouts
        if self.adb_command_timeout <= 0:
            errors.append("adb_command_timeout must be positive")
        if self.ui_wait_timeout <= 0:
            errors.append("ui_wait_timeout must be positive")
        if self.workflow_step_timeout <= 0:
            errors.append("workflow_step_timeout must be positive")
        
        # Validate retries
        if self.max_retries < 0:
            errors.append("max_retries must be non-negative")
        if self.retry_delay < 0:
            errors.append("retry_delay must be non-negative")
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            errors.append(f"log_level must be one of {valid_log_levels}")
        
        # Validate cache TTL
        if self.cache_ttl_seconds < 0:
            errors.append("cache_ttl_seconds must be non-negative")
        
        # Validate PIN requirement
        if self.require_pin and not self.pin_hash:
            errors.append("pin_hash must be set when require_pin is True")
        
        # Validate device allowlist format
        if self.device_allowlist:
            for device_id in self.device_allowlist:
                if not isinstance(device_id, str) or not device_id.strip():
                    errors.append(f"Invalid device ID in allowlist: {device_id}")
        
        return errors
