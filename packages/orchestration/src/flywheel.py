"""
Flywheel
========

The agentic flywheel pattern: Generate -> Test -> Fix -> Repeat
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Callable, Awaitable
from datetime import datetime
import asyncio


@dataclass
class FlywheelConfig:
    """Configuration for the flywheel."""
    max_iterations: int = 5
    timeout_seconds: int = 300
    fail_fast: bool = False
    parallel_gates: bool = True


@dataclass
class FlywheelIteration:
    """Record of a single flywheel iteration."""
    iteration: int
    artifact_version: str
    gate_results: list[dict]
    fixes_applied: list[str]
    duration_ms: int
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FlywheelResult:
    """Result of a flywheel execution."""
    success: bool
    final_artifact: Any
    iterations: list[FlywheelIteration]
    total_duration_ms: int
    failure_reason: Optional[str] = None


class Flywheel:
    """
    The agentic flywheel.

    Runs a generate -> validate -> fix loop until:
    - All gates pass
    - Max iterations reached
    - Timeout exceeded
    """

    def __init__(
        self,
        generator: Callable[[Any], Awaitable[Any]],
        validator: Callable[[Any], Awaitable[list[dict]]],
        fixer: Callable[[Any, list[dict]], Awaitable[Any]],
        config: Optional[FlywheelConfig] = None,
    ):
        """
        Initialize the flywheel.

        Args:
            generator: Async function that generates an artifact from a spec
            validator: Async function that validates an artifact, returns gate results
            fixer: Async function that fixes an artifact based on failed gates
            config: Flywheel configuration
        """
        self.generator = generator
        self.validator = validator
        self.fixer = fixer
        self.config = config or FlywheelConfig()

    async def run(self, spec: Any) -> FlywheelResult:
        """
        Run the flywheel on a spec.

        Args:
            spec: The specification to generate from

        Returns:
            FlywheelResult with final artifact and iteration history
        """
        import time

        start_time = time.monotonic()
        iterations = []
        artifact = None

        try:
            # Initial generation
            artifact = await asyncio.wait_for(
                self.generator(spec),
                timeout=self.config.timeout_seconds,
            )

            for i in range(self.config.max_iterations):
                iter_start = time.monotonic()

                # Validate
                gate_results = await self.validator(artifact)

                # Check if all passed
                all_passed = all(r.get("passed", False) for r in gate_results)
                failed_gates = [r for r in gate_results if not r.get("passed", False)]

                iter_duration = int((time.monotonic() - iter_start) * 1000)

                iteration = FlywheelIteration(
                    iteration=i + 1,
                    artifact_version=f"{spec.name}@{spec.version}-iter{i+1}",
                    gate_results=gate_results,
                    fixes_applied=[],
                    duration_ms=iter_duration,
                )

                if all_passed:
                    iterations.append(iteration)
                    return FlywheelResult(
                        success=True,
                        final_artifact=artifact,
                        iterations=iterations,
                        total_duration_ms=int((time.monotonic() - start_time) * 1000),
                    )

                # Apply fixes
                if self.config.fail_fast and len(failed_gates) > 1:
                    # Only fix first failure
                    failed_gates = failed_gates[:1]

                artifact = await self.fixer(artifact, failed_gates)
                iteration.fixes_applied = [g.get("name", "unknown") for g in failed_gates]
                iterations.append(iteration)

                # Check timeout
                elapsed = time.monotonic() - start_time
                if elapsed > self.config.timeout_seconds:
                    return FlywheelResult(
                        success=False,
                        final_artifact=artifact,
                        iterations=iterations,
                        total_duration_ms=int(elapsed * 1000),
                        failure_reason="Timeout exceeded",
                    )

            # Max iterations reached
            return FlywheelResult(
                success=False,
                final_artifact=artifact,
                iterations=iterations,
                total_duration_ms=int((time.monotonic() - start_time) * 1000),
                failure_reason="Max iterations reached",
            )

        except asyncio.TimeoutError:
            return FlywheelResult(
                success=False,
                final_artifact=artifact,
                iterations=iterations,
                total_duration_ms=int((time.monotonic() - start_time) * 1000),
                failure_reason="Operation timed out",
            )
        except Exception as e:
            return FlywheelResult(
                success=False,
                final_artifact=artifact,
                iterations=iterations,
                total_duration_ms=int((time.monotonic() - start_time) * 1000),
                failure_reason=str(e),
            )


async def create_standard_flywheel(
    inference_client,
    gate_runner,
) -> Flywheel:
    """
    Create a standard flywheel with default generator/validator/fixer.

    Args:
        inference_client: The LLM inference client
        gate_runner: The gate runner for validation

    Returns:
        Configured Flywheel instance
    """
    from ...inference.src.prompts import CodeGenPrompt, RefactorPrompt

    async def generator(spec):
        """Generate code from spec."""
        prompt = CodeGenPrompt(
            task=f"Implement {spec.description}",
            language="python",
            constraints=[
                f"Class: {c.get('name')}" for c in spec.classes
            ] + [
                f"Function: {f.get('name')}" for f in spec.functions
            ],
        )

        result = await inference_client.complete(prompt.render())

        # Parse result into artifact
        from ...shared.src.types import Artifact
        return Artifact(
            name=spec.name,
            version=spec.version,
            spec=spec,
            files={"main.py": result.text},
        )

    async def validator(artifact):
        """Validate artifact through gates."""
        results = gate_runner.run(artifact)
        return [
            {
                "name": r.name,
                "passed": r.passed,
                "message": r.message,
                "details": r.details,
            }
            for r in results
        ]

    async def fixer(artifact, failed_gates):
        """Fix artifact based on failed gates."""
        # Build fix prompt
        failures = "\n".join([
            f"- {g['name']}: {g['message']}"
            for g in failed_gates
        ])

        code = artifact.files.get("main.py", "")

        prompt = f"""Fix the following issues in this code:

{failures}

Current code:
```python
{code}
```

Return only the fixed Python code."""

        result = await inference_client.complete(prompt)

        # Update artifact
        artifact.files["main.py"] = result.text
        return artifact

    return Flywheel(generator, validator, fixer)
