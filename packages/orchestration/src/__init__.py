"""
BLACKICE Orchestration
======================

Flywheel execution and task tracking.

The flywheel pattern: Generate -> Test -> Fix -> Repeat
Until all gates pass or max iterations reached.
"""

from .flywheel import Flywheel, FlywheelConfig, FlywheelResult
from .tasks import Task, TaskTracker, TaskStatus
from .pipeline import Pipeline, PipelineStage

__version__ = "0.1.0"
__all__ = [
    # Flywheel
    "Flywheel",
    "FlywheelConfig",
    "FlywheelResult",
    # Tasks
    "Task",
    "TaskTracker",
    "TaskStatus",
    # Pipeline
    "Pipeline",
    "PipelineStage",
]
