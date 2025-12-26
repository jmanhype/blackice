"""
BLACKICE Shared
===============

Core types, configuration, and utilities used across all packages.
"""

from .types import (
    Spec,
    Artifact,
    ValidationResult,
    GateResult,
    TaskStatus,
    GateStatus,
    FactoryMode,
    SearchResult,
    ExtractionResult,
)
from .config import BlackiceConfig, get_config, set_config
from .logging import get_logger, console

__version__ = "0.1.0"
__all__ = [
    # Types
    "Spec",
    "Artifact",
    "ValidationResult",
    "GateResult",
    "TaskStatus",
    "GateStatus",
    "FactoryMode",
    "SearchResult",
    "ExtractionResult",
    # Config
    "BlackiceConfig",
    "get_config",
    "set_config",
    # Logging
    "get_logger",
    "console",
]
