"""
Core type definitions for BLACKICE.

These types flow through all packages for consistency.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pathlib import Path


class TaskStatus(str, Enum):
    """Status of a factory task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class GateStatus(str, Enum):
    """Status of a quality gate."""
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"


class FactoryMode(str, Enum):
    """Operating mode of the factory."""
    GREENFIELD = "greenfield"  # Generate from spec
    BROWNFIELD = "brownfield"  # Extract spec from code, generate compatible additions
    HYBRID = "hybrid"          # Both modes available


@dataclass
class Spec:
    """
    Specification for what to build.

    Works bidirectionally:
    - Greenfield: Human/LLM writes spec -> factory generates code
    - Brownfield: Factory extracts spec from existing code -> generates compatible additions
    """
    name: str
    version: str
    description: str
    mode: FactoryMode = FactoryMode.GREENFIELD

    # Structure definition
    classes: list[dict] = field(default_factory=list)
    functions: list[dict] = field(default_factory=list)
    endpoints: list[dict] = field(default_factory=list)
    types: list[dict] = field(default_factory=list)

    # Patterns (critical for brownfield compatibility)
    patterns: dict[str, Any] = field(default_factory=dict)
    naming_conventions: dict[str, str] = field(default_factory=dict)
    architectural_style: Optional[str] = None  # e.g., "layered", "hexagonal", "microservices"

    # Dependencies
    dependencies: list[str] = field(default_factory=list)
    dev_dependencies: list[str] = field(default_factory=list)

    # Source tracking (for brownfield)
    extracted_from: Optional[Path] = None
    extracted_at: Optional[datetime] = None
    extraction_confidence: float = 1.0  # 0.0 - 1.0

    # Quality requirements
    gates: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "mode": self.mode.value,
            "classes": self.classes,
            "functions": self.functions,
            "endpoints": self.endpoints,
            "types": self.types,
            "patterns": self.patterns,
            "naming_conventions": self.naming_conventions,
            "architectural_style": self.architectural_style,
            "dependencies": self.dependencies,
            "dev_dependencies": self.dev_dependencies,
            "extracted_from": str(self.extracted_from) if self.extracted_from else None,
            "extracted_at": self.extracted_at.isoformat() if self.extracted_at else None,
            "extraction_confidence": self.extraction_confidence,
            "gates": self.gates,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Spec":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            version=data["version"],
            description=data["description"],
            mode=FactoryMode(data.get("mode", "greenfield")),
            classes=data.get("classes", []),
            functions=data.get("functions", []),
            endpoints=data.get("endpoints", []),
            types=data.get("types", []),
            patterns=data.get("patterns", {}),
            naming_conventions=data.get("naming_conventions", {}),
            architectural_style=data.get("architectural_style"),
            dependencies=data.get("dependencies", []),
            dev_dependencies=data.get("dev_dependencies", []),
            extracted_from=Path(data["extracted_from"]) if data.get("extracted_from") else None,
            extracted_at=datetime.fromisoformat(data["extracted_at"]) if data.get("extracted_at") else None,
            extraction_confidence=data.get("extraction_confidence", 1.0),
            gates=data.get("gates", []),
        )


@dataclass
class Artifact:
    """
    A generated artifact from the factory.
    """
    name: str
    version: str
    spec: Spec

    # Generated content
    files: dict[str, str] = field(default_factory=dict)  # path -> content

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    generator: str = "blackice"
    generator_version: str = "0.1.0"

    # Validation state
    validated: bool = False
    validation_results: list["ValidationResult"] = field(default_factory=list)

    def is_valid(self) -> bool:
        """Check if all validations passed."""
        if not self.validated:
            return False
        return all(r.passed for r in self.validation_results)


@dataclass
class ValidationResult:
    """
    Result of a validation check.
    """
    validator: str
    passed: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[int] = None

    def to_gate_result(self) -> "GateResult":
        """Convert to GateResult for factory gates."""
        return GateResult(
            name=self.validator,
            status=GateStatus.PASS if self.passed else GateStatus.FAIL,
            details=self.details,
            duration_ms=self.duration_ms,
        )


@dataclass
class GateResult:
    """
    Result of a quality gate check.
    """
    name: str
    status: GateStatus
    details: dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[int] = None

    @property
    def passed(self) -> bool:
        """Check if gate passed or was skipped."""
        return self.status in (GateStatus.PASS, GateStatus.SKIP)


@dataclass
class SearchResult:
    """
    Result from a state-space solver search.
    """
    success: bool
    plan: list[str] = field(default_factory=list)
    plan_cost: float = 0.0
    states_explored: int = 0
    final_state: dict[str, Any] = field(default_factory=dict)
    failure_reason: Optional[str] = None
    search_trace: list[dict] = field(default_factory=list)


@dataclass
class ExtractionResult:
    """
    Result from brownfield code extraction.
    """
    source_path: Path
    spec: Spec
    confidence: float  # 0.0 - 1.0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    raw_ast: Optional[dict] = None
    patterns_detected: list[str] = field(default_factory=list)


@dataclass
class GenerationRequest:
    """
    Request to generate code from a spec.
    """
    spec: Spec
    target_language: str = "python"
    target_framework: Optional[str] = None
    output_dir: Optional[Path] = None

    # Generation options
    include_tests: bool = True
    include_docs: bool = True
    style_guide: Optional[str] = None

    # Brownfield compatibility
    must_match_patterns: bool = False  # If True, fail if patterns don't match
    existing_code_path: Optional[Path] = None  # For pattern matching


@dataclass
class GenerationResult:
    """
    Result of code generation.
    """
    success: bool
    artifact: Optional[Artifact] = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    generation_time_ms: int = 0
    tokens_used: int = 0
