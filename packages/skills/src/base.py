"""
Base Skill
==========

Foundation for agent skills.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class SkillContext:
    """Context provided to a skill."""
    spec: Any
    config: dict[str, Any] = field(default_factory=dict)
    history: list[dict] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)


@dataclass
class SkillResult:
    """Result of skill execution."""
    success: bool
    output: Any
    messages: list[str] = field(default_factory=list)
    artifacts: dict[str, str] = field(default_factory=dict)
    next_steps: list[str] = field(default_factory=list)


class Skill(ABC):
    """
    Base class for agent skills.

    A skill encapsulates:
    - System prompt engineering
    - Tool selection
    - Output parsing
    - Error recovery
    """

    name: str = "base"
    description: str = ""
    required_tools: list[str] = []

    @abstractmethod
    def get_system_prompt(self, context: SkillContext) -> str:
        """Get the system prompt for this skill."""
        pass

    @abstractmethod
    def get_user_prompt(self, context: SkillContext) -> str:
        """Get the user prompt to start the skill."""
        pass

    def get_tools(self, context: SkillContext) -> list[str]:
        """Get the tools needed for this skill."""
        return self.required_tools + context.tools

    @abstractmethod
    async def execute(self, context: SkillContext, inference_client) -> SkillResult:
        """Execute the skill."""
        pass

    def parse_output(self, raw_output: str) -> dict[str, Any]:
        """Parse the raw LLM output into structured data."""
        # Default: try to extract code blocks
        import re

        code_blocks = re.findall(r"```(\w+)?\n(.*?)```", raw_output, re.DOTALL)

        if code_blocks:
            return {
                "code_blocks": [
                    {"language": lang or "text", "code": code.strip()}
                    for lang, code in code_blocks
                ],
                "raw": raw_output,
            }

        return {"raw": raw_output}


class SkillRegistry:
    """Registry of available skills."""

    def __init__(self):
        self._skills: dict[str, type[Skill]] = {}

    def register(self, skill_class: type[Skill]) -> type[Skill]:
        """Register a skill class."""
        self._skills[skill_class.name] = skill_class
        return skill_class

    def get(self, name: str) -> Optional[type[Skill]]:
        """Get a skill class by name."""
        return self._skills.get(name)

    def list(self) -> list[str]:
        """List registered skill names."""
        return list(self._skills.keys())

    def create(self, name: str, **kwargs) -> Optional[Skill]:
        """Create a skill instance."""
        skill_class = self.get(name)
        if skill_class:
            return skill_class(**kwargs)
        return None


# Global registry
registry = SkillRegistry()
