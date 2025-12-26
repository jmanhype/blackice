"""
Configuration management for BLACKICE.

Handles environment variables, config files, and runtime settings.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import yaml


@dataclass
class InferenceConfig:
    """Configuration for the inference layer (vLLM)."""
    url: str = "http://localhost:8000"
    model: str = "deepseek-ai/deepseek-coder-6.7b-instruct"
    max_tokens: int = 4096
    temperature: float = 0.1
    timeout_seconds: int = 120

    # GPU settings
    gpu_memory_utilization: float = 0.9
    tensor_parallel_size: int = 1


@dataclass
class MCPConfig:
    """Configuration for MCP servers."""
    servers: dict[str, dict] = field(default_factory=dict)
    default_timeout_ms: int = 30000
    auto_discover: bool = True


@dataclass
class ValidationConfig:
    """Configuration for validation/solvers."""
    max_expansions: int = 100000
    cpsat_time_limit_seconds: int = 60
    enable_tracing: bool = False
    parallel_validators: int = 4


@dataclass
class ExtractionConfig:
    """Configuration for brownfield extraction."""
    languages: list[str] = field(default_factory=lambda: ["python", "javascript", "typescript", "rust"])
    max_file_size_kb: int = 500
    ignore_patterns: list[str] = field(default_factory=lambda: [
        "**/node_modules/**",
        "**/__pycache__/**",
        "**/venv/**",
        "**/.git/**",
        "**/target/**",
        "**/dist/**",
        "**/build/**",
    ])
    extract_patterns: bool = True
    extract_naming: bool = True
    extract_architecture: bool = True


@dataclass
class GenerationConfig:
    """Configuration for code generation."""
    default_language: str = "python"
    include_tests: bool = True
    include_docs: bool = True
    max_retries: int = 3
    flywheel_enabled: bool = True  # Generate -> Test -> Fix loop


@dataclass
class BlackiceConfig:
    """
    Root configuration for BLACKICE.

    Can be loaded from:
    - Environment variables (BLACKICE_*)
    - Config file (blackice.yaml)
    - Runtime overrides
    """
    # Paths
    root: Path = field(default_factory=lambda: Path(os.environ.get("BLACKICE_ROOT", ".")))
    data_dir: Path = field(default_factory=lambda: Path(os.environ.get("BLACKICE_DATA", "./data")))
    cache_dir: Path = field(default_factory=lambda: Path(os.environ.get("BLACKICE_CACHE", "./.blackice")))

    # Mode
    default_mode: str = "hybrid"  # greenfield, brownfield, hybrid

    # Sub-configs
    inference: InferenceConfig = field(default_factory=InferenceConfig)
    mcp: MCPConfig = field(default_factory=MCPConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    extraction: ExtractionConfig = field(default_factory=ExtractionConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)

    # Runtime
    verbose: bool = False
    debug: bool = False

    @classmethod
    def from_file(cls, path: Path) -> "BlackiceConfig":
        """Load configuration from YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> "BlackiceConfig":
        """Create from dictionary."""
        config = cls()

        # Root settings
        if "root" in data:
            config.root = Path(data["root"])
        if "data_dir" in data:
            config.data_dir = Path(data["data_dir"])
        if "cache_dir" in data:
            config.cache_dir = Path(data["cache_dir"])
        if "default_mode" in data:
            config.default_mode = data["default_mode"]
        if "verbose" in data:
            config.verbose = data["verbose"]
        if "debug" in data:
            config.debug = data["debug"]

        # Sub-configs
        if "inference" in data:
            config.inference = InferenceConfig(**data["inference"])
        if "mcp" in data:
            config.mcp = MCPConfig(**data["mcp"])
        if "validation" in data:
            config.validation = ValidationConfig(**data["validation"])
        if "extraction" in data:
            config.extraction = ExtractionConfig(**data["extraction"])
        if "generation" in data:
            config.generation = GenerationConfig(**data["generation"])

        return config

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "root": str(self.root),
            "data_dir": str(self.data_dir),
            "cache_dir": str(self.cache_dir),
            "default_mode": self.default_mode,
            "verbose": self.verbose,
            "debug": self.debug,
            "inference": {
                "url": self.inference.url,
                "model": self.inference.model,
                "max_tokens": self.inference.max_tokens,
                "temperature": self.inference.temperature,
                "timeout_seconds": self.inference.timeout_seconds,
                "gpu_memory_utilization": self.inference.gpu_memory_utilization,
                "tensor_parallel_size": self.inference.tensor_parallel_size,
            },
            "mcp": {
                "servers": self.mcp.servers,
                "default_timeout_ms": self.mcp.default_timeout_ms,
                "auto_discover": self.mcp.auto_discover,
            },
            "validation": {
                "max_expansions": self.validation.max_expansions,
                "cpsat_time_limit_seconds": self.validation.cpsat_time_limit_seconds,
                "enable_tracing": self.validation.enable_tracing,
                "parallel_validators": self.validation.parallel_validators,
            },
            "extraction": {
                "languages": self.extraction.languages,
                "max_file_size_kb": self.extraction.max_file_size_kb,
                "ignore_patterns": self.extraction.ignore_patterns,
                "extract_patterns": self.extraction.extract_patterns,
                "extract_naming": self.extraction.extract_naming,
                "extract_architecture": self.extraction.extract_architecture,
            },
            "generation": {
                "default_language": self.generation.default_language,
                "include_tests": self.generation.include_tests,
                "include_docs": self.generation.include_docs,
                "max_retries": self.generation.max_retries,
                "flywheel_enabled": self.generation.flywheel_enabled,
            },
        }

    def save(self, path: Optional[Path] = None) -> Path:
        """Save configuration to file."""
        if path is None:
            path = self.root / "blackice.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)
        return path


# Global config instance
_config: Optional[BlackiceConfig] = None


def get_config() -> BlackiceConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        # Try to load from file first
        config_path = Path(os.environ.get("BLACKICE_CONFIG", "blackice.yaml"))
        if config_path.exists():
            _config = BlackiceConfig.from_file(config_path)
        else:
            _config = BlackiceConfig()
    return _config


def set_config(config: BlackiceConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config


def reset_config() -> None:
    """Reset the global configuration (useful for testing)."""
    global _config
    _config = None
