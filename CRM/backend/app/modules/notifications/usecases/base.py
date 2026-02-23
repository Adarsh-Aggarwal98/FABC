"""
Base Use Case - Standard result object for use cases
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class UseCaseResult:
    """Standard result object for use cases"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
