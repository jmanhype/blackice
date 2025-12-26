"""
Quality Gates
=============

Enforceable quality checks for generated code.
"""

import subprocess
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Any
import time


@dataclass
class GateResult:
    """Result of a gate check."""
    name: str
    passed: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0


class Gate(ABC):
    """Base class for quality gates."""

    name: str = "base"
    description: str = ""

    @abstractmethod
    def check(self, artifact) -> GateResult:
        """Check if the artifact passes this gate."""
        pass


class SyntaxGate(Gate):
    """Check code syntax validity."""

    name = "syntax"
    description = "Validates code syntax"

    def __init__(self, language: str = "python"):
        self.language = language

    def check(self, artifact) -> GateResult:
        start = time.monotonic()
        errors = []

        for path, content in artifact.files.items():
            if not path.endswith(".py"):
                continue

            try:
                compile(content, path, "exec")
            except SyntaxError as e:
                errors.append(f"{path}:{e.lineno}: {e.msg}")

        duration = int((time.monotonic() - start) * 1000)

        if errors:
            return GateResult(
                name=self.name,
                passed=False,
                message=f"Syntax errors in {len(errors)} locations",
                details={"errors": errors},
                duration_ms=duration,
            )

        return GateResult(
            name=self.name,
            passed=True,
            message="All files have valid syntax",
            duration_ms=duration,
        )


class TypeGate(Gate):
    """Check type correctness with mypy."""

    name = "types"
    description = "Validates type annotations with mypy"

    def __init__(self, strict: bool = False):
        self.strict = strict

    def check(self, artifact) -> GateResult:
        start = time.monotonic()

        # Write files to temp dir
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            for path, content in artifact.files.items():
                if path.endswith(".py"):
                    file_path = tmp_path / path
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(content)

            # Run mypy
            cmd = ["python", "-m", "mypy", str(tmp_path)]
            if self.strict:
                cmd.append("--strict")

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
            except subprocess.TimeoutExpired:
                return GateResult(
                    name=self.name,
                    passed=False,
                    message="Type checking timed out",
                    duration_ms=60000,
                )
            except FileNotFoundError:
                return GateResult(
                    name=self.name,
                    passed=True,
                    message="mypy not installed, skipping",
                    details={"skipped": True},
                    duration_ms=0,
                )

        duration = int((time.monotonic() - start) * 1000)

        if result.returncode == 0:
            return GateResult(
                name=self.name,
                passed=True,
                message="No type errors found",
                duration_ms=duration,
            )

        # Parse errors
        errors = [line for line in result.stdout.split("\n") if line.strip()]

        return GateResult(
            name=self.name,
            passed=False,
            message=f"Type errors: {len(errors)} issues",
            details={"errors": errors[:20]},  # Limit to 20
            duration_ms=duration,
        )


class TestGate(Gate):
    """Run tests and check for failures."""

    name = "tests"
    description = "Runs test suite with pytest"

    def __init__(self, min_coverage: float = 0.0):
        self.min_coverage = min_coverage

    def check(self, artifact) -> GateResult:
        start = time.monotonic()

        # Write files to temp dir
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            for path, content in artifact.files.items():
                file_path = tmp_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)

            # Check if there are test files
            test_files = list(tmp_path.rglob("test_*.py")) + list(tmp_path.rglob("*_test.py"))
            if not test_files:
                return GateResult(
                    name=self.name,
                    passed=True,
                    message="No tests found",
                    details={"skipped": True},
                    duration_ms=0,
                )

            # Run pytest
            cmd = ["python", "-m", "pytest", str(tmp_path), "-v", "--tb=short"]

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=tmp_path,
                )
            except subprocess.TimeoutExpired:
                return GateResult(
                    name=self.name,
                    passed=False,
                    message="Tests timed out",
                    duration_ms=300000,
                )
            except FileNotFoundError:
                return GateResult(
                    name=self.name,
                    passed=True,
                    message="pytest not installed, skipping",
                    details={"skipped": True},
                    duration_ms=0,
                )

        duration = int((time.monotonic() - start) * 1000)

        if result.returncode == 0:
            return GateResult(
                name=self.name,
                passed=True,
                message="All tests passed",
                details={"output": result.stdout[-1000:]},  # Last 1000 chars
                duration_ms=duration,
            )

        return GateResult(
            name=self.name,
            passed=False,
            message="Tests failed",
            details={
                "output": result.stdout[-2000:],
                "errors": result.stderr[-1000:],
            },
            duration_ms=duration,
        )


class PatternGate(Gate):
    """Check if code matches required patterns (for brownfield)."""

    name = "patterns"
    description = "Validates code matches existing patterns"

    def __init__(self, required_patterns: dict[str, str]):
        self.required_patterns = required_patterns

    def check(self, artifact) -> GateResult:
        start = time.monotonic()
        mismatches = []

        # Extract patterns from generated code
        from ...extraction.src.extractor import CodeExtractor
        from ...extraction.src.patterns import PatternDetector

        extractor = CodeExtractor()
        detector = PatternDetector()

        # Write to temp and extract
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            for path, content in artifact.files.items():
                if path.endswith(".py"):
                    file_path = tmp_path / path
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(content)

            # Extract and detect
            try:
                extraction = extractor.extract_file(list(tmp_path.rglob("*.py"))[0])
                report = detector.detect(extraction)

                # Compare patterns
                for pattern_name, expected in self.required_patterns.items():
                    actual = extraction.patterns.get(pattern_name)
                    if actual != expected:
                        mismatches.append({
                            "pattern": pattern_name,
                            "expected": expected,
                            "actual": actual,
                        })
            except Exception as e:
                return GateResult(
                    name=self.name,
                    passed=False,
                    message=f"Pattern extraction failed: {e}",
                    duration_ms=int((time.monotonic() - start) * 1000),
                )

        duration = int((time.monotonic() - start) * 1000)

        if mismatches:
            return GateResult(
                name=self.name,
                passed=False,
                message=f"{len(mismatches)} pattern mismatches",
                details={"mismatches": mismatches},
                duration_ms=duration,
            )

        return GateResult(
            name=self.name,
            passed=True,
            message="All patterns match",
            duration_ms=duration,
        )


class GateRunner:
    """Runs a sequence of gates on an artifact."""

    def __init__(self, gates: Optional[list[Gate]] = None):
        self.gates = gates or [
            SyntaxGate(),
            TypeGate(),
            TestGate(),
        ]

    def run(self, artifact, fail_fast: bool = False) -> list[GateResult]:
        """Run all gates on the artifact."""
        results = []

        for gate in self.gates:
            result = gate.check(artifact)
            results.append(result)

            if fail_fast and not result.passed:
                break

        return results

    def run_all(self, artifact) -> tuple[bool, list[GateResult]]:
        """Run all gates and return overall pass/fail."""
        results = self.run(artifact)
        all_passed = all(r.passed for r in results)
        return all_passed, results
