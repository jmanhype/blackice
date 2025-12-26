"""
Smoke tests for BLACKICE.

Basic tests to verify the packages are importable and functional.
"""

import pytest


class TestImports:
    """Test that all packages are importable."""

    def test_import_shared(self):
        from packages.shared.src import Spec, Artifact, FactoryMode
        assert FactoryMode.GREENFIELD == "greenfield"

    def test_import_inference(self):
        from packages.inference.src import InferenceClient, CodeGenPrompt
        assert InferenceClient is not None

    def test_import_extraction(self):
        from packages.extraction.src import CodeExtractor, PatternDetector
        assert CodeExtractor is not None

    def test_import_validation(self):
        from packages.validation.src import Gate, BFSSolver
        assert Gate is not None

    def test_import_orchestration(self):
        from packages.orchestration.src import Flywheel, TaskTracker, Pipeline
        assert Flywheel is not None

    def test_import_skills(self):
        from packages.skills.src import GreenfieldSkill, BrownfieldSkill
        assert GreenfieldSkill is not None


class TestTypes:
    """Test core types."""

    def test_create_spec(self):
        from packages.shared.src.types import Spec, FactoryMode

        spec = Spec(
            name="test",
            version="1.0.0",
            description="Test spec",
        )
        assert spec.mode == FactoryMode.GREENFIELD

    def test_spec_to_dict(self):
        from packages.shared.src.types import Spec

        spec = Spec(
            name="test",
            version="1.0.0",
            description="Test spec",
            classes=[{"name": "Foo"}],
        )
        data = spec.to_dict()
        assert data["name"] == "test"
        assert data["classes"] == [{"name": "Foo"}]

    def test_spec_from_dict(self):
        from packages.shared.src.types import Spec, FactoryMode

        data = {
            "name": "test",
            "version": "1.0.0",
            "description": "Test",
            "mode": "brownfield",
        }
        spec = Spec.from_dict(data)
        assert spec.mode == FactoryMode.BROWNFIELD


class TestSolver:
    """Test BFS solver."""

    def test_simple_search(self):
        from packages.validation.src.solvers import BFSSolver, State, Action

        # Simple problem: go from 0 to 5 by incrementing
        initial = State(data={"value": 0})

        def goal(s):
            return s.data["value"] == 5

        def can_increment(s):
            return s.data["value"] < 10

        def do_increment(s):
            return State(data={"value": s.data["value"] + 1})

        actions = [
            Action(
                name="increment",
                preconditions=can_increment,
                effects=do_increment,
            )
        ]

        solver = BFSSolver(max_expansions=100)
        result = solver.solve(initial, goal, actions)

        assert result.success
        assert result.plan == ["increment"] * 5
        assert result.final_state.data["value"] == 5


class TestExtraction:
    """Test code extraction."""

    def test_extract_class(self):
        from packages.extraction.src.extractor import CodeExtractor
        from pathlib import Path
        import tempfile

        code = '''
class MyClass:
    """A test class."""

    def my_method(self):
        pass
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()

            extractor = CodeExtractor("python")
            result = extractor.extract_file(Path(f.name))

            assert len(result.classes) == 1
            assert result.classes[0].name == "MyClass"
            assert "my_method" in result.classes[0].methods
