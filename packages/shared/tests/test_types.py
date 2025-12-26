"""Tests for core types."""

import pytest
from pathlib import Path
from datetime import datetime

from src.types import (
    Spec,
    Artifact,
    FactoryMode,
    TaskStatus,
    GateStatus,
    ValidationResult,
    GateResult,
)


class TestSpec:
    def test_create_greenfield_spec(self):
        spec = Spec(
            name="test-service",
            version="1.0.0",
            description="A test service",
        )
        assert spec.mode == FactoryMode.GREENFIELD
        assert spec.classes == []
        assert spec.patterns == {}

    def test_create_brownfield_spec(self):
        spec = Spec(
            name="extracted-service",
            version="1.0.0",
            description="Extracted from existing code",
            mode=FactoryMode.BROWNFIELD,
            extracted_from=Path("/some/path"),
            extraction_confidence=0.85,
        )
        assert spec.mode == FactoryMode.BROWNFIELD
        assert spec.extraction_confidence == 0.85

    def test_spec_to_dict(self):
        spec = Spec(
            name="test",
            version="1.0.0",
            description="Test",
            classes=[{"name": "Foo"}],
        )
        data = spec.to_dict()
        assert data["name"] == "test"
        assert data["classes"] == [{"name": "Foo"}]
        assert data["mode"] == "greenfield"

    def test_spec_from_dict(self):
        data = {
            "name": "test",
            "version": "1.0.0",
            "description": "Test",
            "mode": "brownfield",
            "patterns": {"error_handling": "exceptions"},
        }
        spec = Spec.from_dict(data)
        assert spec.name == "test"
        assert spec.mode == FactoryMode.BROWNFIELD
        assert spec.patterns["error_handling"] == "exceptions"


class TestArtifact:
    def test_create_artifact(self):
        spec = Spec(name="test", version="1.0.0", description="Test")
        artifact = Artifact(
            name="test",
            version="1.0.0",
            spec=spec,
            files={"main.py": "print('hello')"},
        )
        assert artifact.generator == "blackice"
        assert "main.py" in artifact.files

    def test_is_valid_unvalidated(self):
        spec = Spec(name="test", version="1.0.0", description="Test")
        artifact = Artifact(name="test", version="1.0.0", spec=spec)
        assert not artifact.is_valid()

    def test_is_valid_passed(self):
        spec = Spec(name="test", version="1.0.0", description="Test")
        artifact = Artifact(
            name="test",
            version="1.0.0",
            spec=spec,
            validated=True,
            validation_results=[
                ValidationResult(validator="syntax", passed=True, message="OK"),
                ValidationResult(validator="types", passed=True, message="OK"),
            ],
        )
        assert artifact.is_valid()

    def test_is_valid_failed(self):
        spec = Spec(name="test", version="1.0.0", description="Test")
        artifact = Artifact(
            name="test",
            version="1.0.0",
            spec=spec,
            validated=True,
            validation_results=[
                ValidationResult(validator="syntax", passed=True, message="OK"),
                ValidationResult(validator="types", passed=False, message="Type error"),
            ],
        )
        assert not artifact.is_valid()


class TestValidationResult:
    def test_to_gate_result_pass(self):
        result = ValidationResult(
            validator="syntax",
            passed=True,
            message="All good",
        )
        gate = result.to_gate_result()
        assert gate.status == GateStatus.PASS
        assert gate.passed

    def test_to_gate_result_fail(self):
        result = ValidationResult(
            validator="types",
            passed=False,
            message="Type mismatch",
        )
        gate = result.to_gate_result()
        assert gate.status == GateStatus.FAIL
        assert not gate.passed


class TestGateResult:
    def test_passed_on_pass(self):
        gate = GateResult(name="test", status=GateStatus.PASS)
        assert gate.passed

    def test_passed_on_skip(self):
        gate = GateResult(name="test", status=GateStatus.SKIP)
        assert gate.passed

    def test_not_passed_on_fail(self):
        gate = GateResult(name="test", status=GateStatus.FAIL)
        assert not gate.passed

    def test_not_passed_on_error(self):
        gate = GateResult(name="test", status=GateStatus.ERROR)
        assert not gate.passed
