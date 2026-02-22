"""Text processing utilities."""

import re
import shlex
from typing import Optional


def escape_shell_text(text: str) -> str:
    """
    Escape text for shell input.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text safe for shell
    """
    return shlex.quote(text)


def extract_otp_from_text(text: str) -> Optional[str]:
    """
    Extract OTP code from text using regex.
    
    Args:
        text: Text containing OTP
        
    Returns:
        OTP code if found, None otherwise
    """
    # Try different OTP patterns
    patterns = [
        r'\b(\d{6})\b',  # 6 digits
        r'\b(\d{4})\b',  # 4 digits
        r'\b(\d{8})\b',  # 8 digits
        r'(?:OTP|code|verification)[\s:]+(\d{4,8})',  # With keywords
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


def normalize_app_name(app_name: str) -> str:
    """
    Normalize app name to package identifier.
    
    Args:
        app_name: Friendly app name
        
    Returns:
        Package identifier or original name if not found
    """
    from mcp_server.app_actions import APP_REGISTRY
    
    app_name_lower = app_name.lower().strip()
    return APP_REGISTRY.get(app_name_lower, app_name)
