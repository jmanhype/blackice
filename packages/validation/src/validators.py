"""
Validators
==========

Composable validation pipelines.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
import asyncio


@dataclass
class ValidationResult:
    """Result of a validation."""
    validator: str
    passed: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0
    severity: str = "error"  # error, warning, info


class Validator(ABC):
    """Base class for validators."""

    name: str = "base"

    @abstractmethod
    async def validate(self, artifact) -> ValidationResult:
        """Validate an artifact."""
        pass


class SyntaxValidator(Validator):
    """Validates Python syntax."""

    name = "syntax"

    async def validate(self, artifact) -> ValidationResult:
        errors = []

        for path, content in artifact.files.items():
            if not path.endswith(".py"):
                continue
            try:
                compile(content, path, "exec")
            except SyntaxError as e:
                errors.append(f"{path}:{e.lineno}: {e.msg}")

        if errors:
            return ValidationResult(
                validator=self.name,
                passed=False,
                message=f"{len(errors)} syntax errors",
                details={"errors": errors},
            )

        return ValidationResult(
            validator=self.name,
            passed=True,
            message="Valid syntax",
        )


class ImportValidator(Validator):
    """Validates that imports are resolvable."""

    name = "imports"

    def __init__(self, allowed_missing: Optional[list[str]] = None):
        self.allowed_missing = allowed_missing or []

    async def validate(self, artifact) -> ValidationResult:
        import ast
        import importlib.util

        missing = []

        for path, content in artifact.files.items():
            if not path.endswith(".py"):
                continue

            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name.split(".")[0]
                        if module not in self.allowed_missing:
                            if importlib.util.find_spec(module) is None:
                                missing.append(module)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module = node.module.split(".")[0]
                        if module not in self.allowed_missing:
                            if importlib.util.find_spec(module) is None:
                                missing.append(module)

        missing = list(set(missing))

        if missing:
            return ValidationResult(
                validator=self.name,
                passed=False,
                message=f"{len(missing)} unresolvable imports",
                details={"missing": missing},
            )

        return ValidationResult(
            validator=self.name,
            passed=True,
            message="All imports resolvable",
        )


class DocstringValidator(Validator):
    """Validates that public functions have docstrings."""

    name = "docstrings"

    async def validate(self, artifact) -> ValidationResult:
        import ast

        missing = []

        for path, content in artifact.files.items():
            if not path.endswith(".py"):
                continue

            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Skip private functions
                    if node.name.startswith("_"):
                        continue

                    # Check for docstring
                    docstring = ast.get_docstring(node)
                    if not docstring:
                        missing.append(f"{path}:{node.name}")

        if missing:
            return ValidationResult(
                validator=self.name,
                passed=False,
                message=f"{len(missing)} functions missing docstrings",
                details={"missing": missing[:20]},
                severity="warning",
            )

        return ValidationResult(
            validator=self.name,
            passed=True,
            message="All public functions have docstrings",
        )


class NamingValidator(Validator):
    """Validates naming conventions."""

    name = "naming"

    def __init__(self, conventions: Optional[dict[str, str]] = None):
        self.conventions = conventions or {
            "classes": "PascalCase",
            "functions": "snake_case",
        }

    async def validate(self, artifact) -> ValidationResult:
        import ast
        import re

        violations = []

        patterns = {
            "PascalCase": r"^[A-Z][a-zA-Z0-9]*$",
            "snake_case": r"^[a-z_][a-z0-9_]*$",
            "camelCase": r"^[a-z][a-zA-Z0-9]*$",
        }

        for path, content in artifact.files.items():
            if not path.endswith(".py"):
                continue

            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    expected = self.conventions.get("classes", "PascalCase")
                    pattern = patterns.get(expected, ".*")
                    if not re.match(pattern, node.name):
                        violations.append(f"{path}: class {node.name} should be {expected}")

                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not node.name.startswith("_"):
                        expected = self.conventions.get("functions", "snake_case")
                        pattern = patterns.get(expected, ".*")
                        if not re.match(pattern, node.name):
                            violations.append(f"{path}: function {node.name} should be {expected}")

        if violations:
            return ValidationResult(
                validator=self.name,
                passed=False,
                message=f"{len(violations)} naming violations",
                details={"violations": violations[:20]},
                severity="warning",
            )

        return ValidationResult(
            validator=self.name,
            passed=True,
            message="All names follow conventions",
        )


class ValidationPipeline:
    """
    Runs multiple validators in parallel.
    """

    def __init__(self, validators: Optional[list[Validator]] = None):
        self.validators = validators or [
            SyntaxValidator(),
            ImportValidator(),
            DocstringValidator(),
            NamingValidator(),
        ]

    async def validate(self, artifact) -> list[ValidationResult]:
        """Run all validators on the artifact."""
        tasks = [v.validate(artifact) for v in self.validators]
        results = await asyncio.gather(*tasks)
        return list(results)

    async def validate_all(self, artifact) -> tuple[bool, list[ValidationResult]]:
        """Validate and return pass/fail status."""
        results = await self.validate(artifact)
        # Only fail on errors, not warnings
        all_passed = all(
            r.passed or r.severity != "error"
            for r in results
        )
        return all_passed, results
