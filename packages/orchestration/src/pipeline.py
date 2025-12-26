"""
Pipeline
========

Multi-stage execution pipelines.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable, Optional
from enum import Enum
import asyncio
import time


class StageStatus(str, Enum):
    """Status of a pipeline stage."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StageResult:
    """Result of a pipeline stage."""
    name: str
    status: StageStatus
    output: Any = None
    error: Optional[str] = None
    duration_ms: int = 0


@dataclass
class PipelineStage:
    """A stage in the pipeline."""
    name: str
    handler: Callable[[Any], Awaitable[Any]]
    skip_on_failure: bool = False
    timeout_seconds: int = 60
    retries: int = 0


@dataclass
class PipelineResult:
    """Result of a pipeline execution."""
    success: bool
    stages: list[StageResult]
    final_output: Any = None
    total_duration_ms: int = 0


class Pipeline:
    """
    Multi-stage execution pipeline.

    Stages run in sequence, with output of each stage
    passed as input to the next.
    """

    def __init__(self, stages: Optional[list[PipelineStage]] = None):
        self.stages = stages or []

    def add_stage(
        self,
        name: str,
        handler: Callable[[Any], Awaitable[Any]],
        **kwargs,
    ) -> "Pipeline":
        """Add a stage to the pipeline."""
        self.stages.append(PipelineStage(name=name, handler=handler, **kwargs))
        return self

    async def run(self, initial_input: Any = None) -> PipelineResult:
        """Run the pipeline."""
        start_time = time.monotonic()
        results = []
        current_input = initial_input
        success = True

        for stage in self.stages:
            stage_start = time.monotonic()

            try:
                # Run with timeout and retries
                output = None
                last_error = None

                for attempt in range(stage.retries + 1):
                    try:
                        output = await asyncio.wait_for(
                            stage.handler(current_input),
                            timeout=stage.timeout_seconds,
                        )
                        last_error = None
                        break
                    except Exception as e:
                        last_error = str(e)
                        if attempt < stage.retries:
                            await asyncio.sleep(1)  # Brief delay before retry

                if last_error:
                    raise Exception(last_error)

                duration = int((time.monotonic() - stage_start) * 1000)
                results.append(StageResult(
                    name=stage.name,
                    status=StageStatus.COMPLETED,
                    output=output,
                    duration_ms=duration,
                ))
                current_input = output

            except asyncio.TimeoutError:
                duration = int((time.monotonic() - stage_start) * 1000)
                results.append(StageResult(
                    name=stage.name,
                    status=StageStatus.FAILED,
                    error="Timeout",
                    duration_ms=duration,
                ))
                success = False

                if not stage.skip_on_failure:
                    break

            except Exception as e:
                duration = int((time.monotonic() - stage_start) * 1000)
                results.append(StageResult(
                    name=stage.name,
                    status=StageStatus.FAILED,
                    error=str(e),
                    duration_ms=duration,
                ))
                success = False

                if not stage.skip_on_failure:
                    break

        # Mark remaining stages as skipped
        completed_names = {r.name for r in results}
        for stage in self.stages:
            if stage.name not in completed_names:
                results.append(StageResult(
                    name=stage.name,
                    status=StageStatus.SKIPPED,
                ))

        total_duration = int((time.monotonic() - start_time) * 1000)

        return PipelineResult(
            success=success,
            stages=results,
            final_output=current_input if success else None,
            total_duration_ms=total_duration,
        )


def create_generation_pipeline() -> Pipeline:
    """Create a standard code generation pipeline."""
    return Pipeline([
        PipelineStage(
            name="parse_spec",
            handler=lambda spec: spec,  # Placeholder
            timeout_seconds=10,
        ),
        PipelineStage(
            name="generate_code",
            handler=lambda spec: spec,  # Placeholder
            timeout_seconds=120,
            retries=2,
        ),
        PipelineStage(
            name="validate_syntax",
            handler=lambda artifact: artifact,  # Placeholder
            timeout_seconds=30,
        ),
        PipelineStage(
            name="run_tests",
            handler=lambda artifact: artifact,  # Placeholder
            timeout_seconds=300,
            skip_on_failure=True,  # Continue even if tests fail
        ),
        PipelineStage(
            name="check_types",
            handler=lambda artifact: artifact,  # Placeholder
            timeout_seconds=60,
            skip_on_failure=True,
        ),
    ])


def create_brownfield_pipeline() -> Pipeline:
    """Create a brownfield extraction and generation pipeline."""
    return Pipeline([
        PipelineStage(
            name="scan_codebase",
            handler=lambda path: path,  # Placeholder
            timeout_seconds=60,
        ),
        PipelineStage(
            name="extract_patterns",
            handler=lambda scan: scan,  # Placeholder
            timeout_seconds=30,
        ),
        PipelineStage(
            name="build_spec",
            handler=lambda patterns: patterns,  # Placeholder
            timeout_seconds=30,
        ),
        PipelineStage(
            name="generate_compatible_code",
            handler=lambda spec: spec,  # Placeholder
            timeout_seconds=120,
            retries=2,
        ),
        PipelineStage(
            name="validate_compatibility",
            handler=lambda artifact: artifact,  # Placeholder
            timeout_seconds=60,
        ),
    ])
