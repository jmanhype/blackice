"""
BLACKICE Dispatcher

Routes tasks to the appropriate backend:
- ai-factory: Deterministic solvers, gates, traces
- speckit: Spec-driven workflow phases
- LLM tools: Pattern matching, generation, refinement
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import subprocess
import json
from pathlib import Path


class Backend(Enum):
    AI_FACTORY = "ai-factory"
    SPECKIT = "speckit"
    LLM = "llm"


@dataclass
class Task:
    """A task to be dispatched."""
    description: str
    task_type: str
    inputs: dict
    backend_hint: Optional[Backend] = None


@dataclass
class DispatchResult:
    """Result from dispatching a task."""
    backend: Backend
    success: bool
    output: dict
    trace_id: Optional[str] = None


class Dispatcher:
    """
    Routes tasks to appropriate backends based on task characteristics.

    Decision logic:
    - Optimization/planning problems → ai-factory (BFS/CP-SAT)
    - Spec-driven features → speckit (phases)
    - Text generation/refinement → LLM tools
    """

    def __init__(
        self,
        factory_root: Optional[Path] = None,
        speckit_root: Optional[Path] = None,
    ):
        self.factory_root = factory_root or Path.home() / "ai-factory"
        self.speckit_root = speckit_root or Path.home() / "speckit"

    def classify(self, task: Task) -> Backend:
        """Classify which backend should handle this task."""

        # Explicit hint takes priority
        if task.backend_hint:
            return task.backend_hint

        # Keywords suggesting deterministic solving
        deterministic_keywords = [
            "optimize", "solve", "plan", "schedule", "route",
            "minimize", "maximize", "constraint", "puzzle",
            "validate", "verify", "prove", "gate"
        ]

        # Keywords suggesting spec workflow
        spec_keywords = [
            "feature", "specify", "requirement", "user story",
            "acceptance criteria", "clarify", "implement"
        ]

        # Keywords suggesting LLM
        llm_keywords = [
            "generate", "write", "refactor", "explain",
            "summarize", "translate", "creative"
        ]

        desc_lower = task.description.lower()

        # Score each backend
        scores = {
            Backend.AI_FACTORY: sum(1 for k in deterministic_keywords if k in desc_lower),
            Backend.SPECKIT: sum(1 for k in spec_keywords if k in desc_lower),
            Backend.LLM: sum(1 for k in llm_keywords if k in desc_lower),
        }

        # Return highest scoring, default to LLM for ties
        return max(scores, key=lambda b: (scores[b], b == Backend.LLM))

    def dispatch(self, task: Task) -> DispatchResult:
        """Dispatch task to appropriate backend."""

        backend = self.classify(task)

        if backend == Backend.AI_FACTORY:
            return self._dispatch_factory(task)
        elif backend == Backend.SPECKIT:
            return self._dispatch_speckit(task)
        else:
            return self._dispatch_llm(task)

    def _dispatch_factory(self, task: Task) -> DispatchResult:
        """Dispatch to ai-factory."""

        # Create task YAML for factory
        task_yaml = {
            "metadata": {
                "name": task.description[:50].replace(" ", "-").lower(),
                "version": "0.1.0",
            },
            "job": {
                "inputs": task.inputs,
            }
        }

        # In production, would write to factory tasks/ and run
        # For now, return placeholder
        return DispatchResult(
            backend=Backend.AI_FACTORY,
            success=True,
            output={"task_yaml": task_yaml, "status": "created"},
            trace_id=None,  # Would be populated after run
        )

    def _dispatch_speckit(self, task: Task) -> DispatchResult:
        """Dispatch to speckit workflow."""

        # Determine which phase to invoke
        desc_lower = task.description.lower()

        if "specify" in desc_lower or "feature" in desc_lower:
            phase = "specify"
        elif "plan" in desc_lower:
            phase = "plan"
        elif "implement" in desc_lower:
            phase = "implement"
        else:
            phase = "specify"  # Default to start

        return DispatchResult(
            backend=Backend.SPECKIT,
            success=True,
            output={"phase": phase, "command": f"/speckit.{phase}"},
        )

    def _dispatch_llm(self, task: Task) -> DispatchResult:
        """Dispatch to LLM tools."""

        return DispatchResult(
            backend=Backend.LLM,
            success=True,
            output={
                "prompt": task.description,
                "inputs": task.inputs,
                "suggested_model": "deepseek-coder-6.7b-instruct",
            },
        )


# Convenience function
def dispatch(description: str, **inputs) -> DispatchResult:
    """Quick dispatch a task."""
    dispatcher = Dispatcher()
    task = Task(description=description, task_type="auto", inputs=inputs)
    return dispatcher.dispatch(task)


if __name__ == "__main__":
    # Example usage
    examples = [
        "Optimize the delivery route for 10 stops",
        "Specify a new user authentication feature",
        "Generate unit tests for the User class",
        "Validate the plan meets all constraints",
    ]

    dispatcher = Dispatcher()

    for desc in examples:
        task = Task(description=desc, task_type="auto", inputs={})
        result = dispatcher.dispatch(task)
        print(f"\n{desc}")
        print(f"  → Backend: {result.backend.value}")
        print(f"  → Output: {result.output}")
