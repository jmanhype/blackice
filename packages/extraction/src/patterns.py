"""
Pattern Detection
=================

Detects architectural and coding patterns in existing code.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum


class PatternCategory(str, Enum):
    """Categories of patterns."""
    ARCHITECTURE = "architecture"
    ERROR_HANDLING = "error_handling"
    CONCURRENCY = "concurrency"
    DATA_MODELING = "data_modeling"
    TESTING = "testing"
    LOGGING = "logging"
    DEPENDENCY_INJECTION = "dependency_injection"


@dataclass
class Pattern:
    """A detected pattern."""
    name: str
    category: PatternCategory
    confidence: float  # 0.0 - 1.0
    evidence: list[str] = field(default_factory=list)
    description: Optional[str] = None


@dataclass
class PatternReport:
    """Report of all detected patterns."""
    patterns: list[Pattern] = field(default_factory=list)
    architecture: Optional[str] = None
    style_summary: dict[str, Any] = field(default_factory=dict)


class PatternDetector:
    """
    Detects patterns in code based on extraction results.
    """

    def __init__(self):
        self.detectors = [
            self._detect_error_handling,
            self._detect_logging,
            self._detect_di,
            self._detect_testing,
            self._detect_architecture,
        ]

    def detect(self, extraction_result) -> PatternReport:
        """Detect patterns from extraction result."""
        patterns = []

        for detector in self.detectors:
            detected = detector(extraction_result)
            patterns.extend(detected)

        # Determine overall architecture
        architecture = self._determine_architecture(extraction_result, patterns)

        # Build style summary
        style = self._build_style_summary(extraction_result, patterns)

        return PatternReport(
            patterns=patterns,
            architecture=architecture,
            style_summary=style,
        )

    def _detect_error_handling(self, result) -> list[Pattern]:
        """Detect error handling patterns."""
        patterns = []

        # Check imports for Result types
        result_imports = [i for i in result.imports if "result" in i.module.lower()]
        if result_imports:
            patterns.append(Pattern(
                name="Result Types",
                category=PatternCategory.ERROR_HANDLING,
                confidence=0.9,
                evidence=[f"import {i.module}" for i in result_imports],
                description="Uses Result/Either types for error handling",
            ))

        # Check for exception classes
        exception_classes = [c for c in result.classes if any("Exception" in b or "Error" in b for b in c.bases)]
        if exception_classes:
            patterns.append(Pattern(
                name="Custom Exceptions",
                category=PatternCategory.ERROR_HANDLING,
                confidence=0.85,
                evidence=[c.name for c in exception_classes],
                description="Defines custom exception types",
            ))

        return patterns

    def _detect_logging(self, result) -> list[Pattern]:
        """Detect logging patterns."""
        patterns = []

        # Check for logging imports
        logging_imports = [i for i in result.imports if i.module in ("logging", "structlog", "loguru")]
        if logging_imports:
            module = logging_imports[0].module
            patterns.append(Pattern(
                name=f"{module.title()} Logging",
                category=PatternCategory.LOGGING,
                confidence=0.9,
                evidence=[f"import {module}"],
                description=f"Uses {module} for logging",
            ))

        return patterns

    def _detect_di(self, result) -> list[Pattern]:
        """Detect dependency injection patterns."""
        patterns = []

        # Check for DI framework imports
        di_frameworks = ["dependency_injector", "injector", "punq", "di"]
        di_imports = [i for i in result.imports if any(di in i.module for di in di_frameworks)]
        if di_imports:
            patterns.append(Pattern(
                name="DI Framework",
                category=PatternCategory.DEPENDENCY_INJECTION,
                confidence=0.95,
                evidence=[i.module for i in di_imports],
                description="Uses a DI framework",
            ))

        # Check for constructor injection pattern
        init_with_deps = []
        for cls in result.classes:
            if "__init__" in cls.methods:
                # Simple heuristic: if init takes multiple typed params, might be DI
                init_with_deps.append(cls.name)

        if len(init_with_deps) > len(result.classes) * 0.3:
            patterns.append(Pattern(
                name="Constructor Injection",
                category=PatternCategory.DEPENDENCY_INJECTION,
                confidence=0.7,
                evidence=init_with_deps[:5],  # First 5 examples
                description="Uses constructor injection pattern",
            ))

        return patterns

    def _detect_testing(self, result) -> list[Pattern]:
        """Detect testing patterns."""
        patterns = []

        # Check for test framework imports
        test_frameworks = {
            "pytest": "pytest",
            "unittest": "unittest",
            "nose": "nose",
        }

        for module, name in test_frameworks.items():
            if any(i.module.startswith(module) for i in result.imports):
                patterns.append(Pattern(
                    name=f"{name.title()} Testing",
                    category=PatternCategory.TESTING,
                    confidence=0.95,
                    evidence=[f"import {module}"],
                    description=f"Uses {name} for testing",
                ))
                break

        # Check for mock usage
        mock_imports = [i for i in result.imports if "mock" in i.module.lower()]
        if mock_imports:
            patterns.append(Pattern(
                name="Mocking",
                category=PatternCategory.TESTING,
                confidence=0.9,
                evidence=[i.module for i in mock_imports],
                description="Uses mocking for tests",
            ))

        return patterns

    def _detect_architecture(self, result) -> list[Pattern]:
        """Detect architectural patterns."""
        patterns = []

        # Check for common architectural indicators
        class_names = [c.name.lower() for c in result.classes]

        # Repository pattern
        if any("repository" in n for n in class_names):
            patterns.append(Pattern(
                name="Repository Pattern",
                category=PatternCategory.ARCHITECTURE,
                confidence=0.85,
                evidence=[c.name for c in result.classes if "repository" in c.name.lower()],
                description="Uses repository pattern for data access",
            ))

        # Service pattern
        if any("service" in n for n in class_names):
            patterns.append(Pattern(
                name="Service Pattern",
                category=PatternCategory.ARCHITECTURE,
                confidence=0.85,
                evidence=[c.name for c in result.classes if "service" in c.name.lower()],
                description="Uses service layer pattern",
            ))

        # Controller/Handler pattern
        if any("controller" in n or "handler" in n for n in class_names):
            patterns.append(Pattern(
                name="Controller Pattern",
                category=PatternCategory.ARCHITECTURE,
                confidence=0.85,
                evidence=[c.name for c in result.classes if "controller" in c.name.lower() or "handler" in c.name.lower()],
                description="Uses controller/handler pattern",
            ))

        return patterns

    def _determine_architecture(self, result, patterns: list[Pattern]) -> Optional[str]:
        """Determine the overall architectural style."""
        pattern_names = {p.name for p in patterns if p.category == PatternCategory.ARCHITECTURE}

        if "Repository Pattern" in pattern_names and "Service Pattern" in pattern_names:
            if "Controller Pattern" in pattern_names:
                return "layered"
            return "clean"

        if any("port" in c.name.lower() or "adapter" in c.name.lower() for c in result.classes):
            return "hexagonal"

        return None

    def _build_style_summary(self, result, patterns: list[Pattern]) -> dict[str, Any]:
        """Build a summary of the code style."""
        return {
            "naming": result.naming_conventions,
            "patterns": result.patterns,
            "has_types": any(f.return_type for f in result.functions),
            "uses_async": any(f.is_async for f in result.functions),
            "detected_patterns": [p.name for p in patterns],
        }
