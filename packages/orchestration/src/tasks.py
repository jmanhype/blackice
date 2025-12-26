"""
Task Tracking
=============

Git-backed task management (like Beads).
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional
import json


class TaskStatus(str, Enum):
    """Status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class Task:
    """A tracked task."""
    id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 0  # Lower = higher priority
    tags: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority,
            "tags": self.tags,
            "dependencies": self.dependencies,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            status=TaskStatus(data.get("status", "pending")),
            priority=data.get("priority", 0),
            tags=data.get("tags", []),
            dependencies=data.get("dependencies", []),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.utcnow(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.utcnow(),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            metadata=data.get("metadata", {}),
        )


class TaskTracker:
    """
    Git-backed task tracker.

    Stores tasks in a JSON file that can be committed with code.
    """

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self._tasks: dict[str, Task] = {}
        self._load()

    def _load(self):
        """Load tasks from storage."""
        if self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text())
                self._tasks = {
                    t["id"]: Task.from_dict(t)
                    for t in data.get("tasks", [])
                }
            except (json.JSONDecodeError, KeyError):
                self._tasks = {}

    def _save(self):
        """Save tasks to storage."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "1.0",
            "updated_at": datetime.utcnow().isoformat(),
            "tasks": [t.to_dict() for t in self._tasks.values()],
        }
        self.storage_path.write_text(json.dumps(data, indent=2))

    def add(self, task: Task) -> Task:
        """Add a task."""
        self._tasks[task.id] = task
        self._save()
        return task

    def get(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    def update(self, task_id: str, **updates) -> Optional[Task]:
        """Update a task."""
        task = self._tasks.get(task_id)
        if not task:
            return None

        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)

        task.updated_at = datetime.utcnow()

        if updates.get("status") == TaskStatus.COMPLETED:
            task.completed_at = datetime.utcnow()

        self._save()
        return task

    def delete(self, task_id: str) -> bool:
        """Delete a task."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            self._save()
            return True
        return False

    def list(
        self,
        status: Optional[TaskStatus] = None,
        tags: Optional[list[str]] = None,
    ) -> list[Task]:
        """List tasks with optional filters."""
        tasks = list(self._tasks.values())

        if status:
            tasks = [t for t in tasks if t.status == status]

        if tags:
            tasks = [t for t in tasks if any(tag in t.tags for tag in tags)]

        # Sort by priority, then by created_at
        tasks.sort(key=lambda t: (t.priority, t.created_at))

        return tasks

    def get_next(self) -> Optional[Task]:
        """Get the next task to work on."""
        pending = self.list(status=TaskStatus.PENDING)

        # Filter out blocked tasks
        ready = []
        for task in pending:
            if not task.dependencies:
                ready.append(task)
            else:
                # Check if all dependencies are completed
                deps_completed = all(
                    self._tasks.get(dep_id, Task(id="", title="")).status == TaskStatus.COMPLETED
                    for dep_id in task.dependencies
                )
                if deps_completed:
                    ready.append(task)

        return ready[0] if ready else None

    def start(self, task_id: str) -> Optional[Task]:
        """Start working on a task."""
        return self.update(task_id, status=TaskStatus.IN_PROGRESS)

    def complete(self, task_id: str) -> Optional[Task]:
        """Mark a task as completed."""
        return self.update(task_id, status=TaskStatus.COMPLETED)

    def fail(self, task_id: str, reason: str = "") -> Optional[Task]:
        """Mark a task as failed."""
        return self.update(
            task_id,
            status=TaskStatus.FAILED,
            metadata={"failure_reason": reason},
        )

    def stats(self) -> dict[str, int]:
        """Get task statistics."""
        stats = {status.value: 0 for status in TaskStatus}
        for task in self._tasks.values():
            stats[task.status.value] += 1
        return stats
