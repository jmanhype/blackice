"""
Refactor Skill
==============

Refactor code to match target patterns.
"""

from dataclasses import dataclass
from typing import Any

from .base import Skill, SkillContext, SkillResult, registry


@registry.register
class RefactorSkill(Skill):
    """
    Refactor code to match target patterns.

    Useful for:
    - Migrating code to new patterns
    - Fixing style inconsistencies
    - Updating to new conventions
    """

    name = "refactor"
    description = "Refactor code to match target patterns"
    required_tools = ["read_file", "write_file"]

    def __init__(self, target_patterns: dict[str, str] = None):
        self.target_patterns = target_patterns or {}

    def get_system_prompt(self, context: SkillContext) -> str:
        return f"""You are an expert software engineer performing code refactoring.

## Target Patterns
{self._format_target_patterns()}

## Refactoring Rules
1. PRESERVE all existing functionality
2. MATCH the target patterns exactly
3. MAINTAIN test coverage
4. KEEP backward compatibility where possible
5. DOCUMENT any breaking changes

## Output Format
Provide the refactored code with comments explaining significant changes.
"""

    def get_user_prompt(self, context: SkillContext) -> str:
        code = context.config.get("code", "")
        return f"""Refactor this code to match the target patterns:

```python
{code}
```

Provide the complete refactored code."""

    async def execute(self, context: SkillContext, inference_client) -> SkillResult:
        """Execute refactoring."""
        system_prompt = self.get_system_prompt(context)
        user_prompt = self.get_user_prompt(context)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        result = await inference_client.chat(messages)
        parsed = self.parse_output(result.text)

        # Extract refactored code
        artifacts = {}
        for i, block in enumerate(parsed.get("code_blocks", [])):
            if block["language"] == "python":
                artifacts["refactored.py"] = block["code"]
                break

        return SkillResult(
            success=True,
            output=parsed,
            artifacts=artifacts,
            next_steps=[
                "Diff against original",
                "Run tests",
                "Review changes",
            ],
        )

    def _format_target_patterns(self) -> str:
        if not self.target_patterns:
            return "Use modern Python best practices"

        lines = []
        for pattern, value in self.target_patterns.items():
            lines.append(f"- {pattern}: {value}")
        return "\n".join(lines)


@registry.register
class TestGenSkill(Skill):
    """Generate tests for code."""

    name = "testgen"
    description = "Generate tests for code"
    required_tools = ["read_file", "write_file"]

    def __init__(self, framework: str = "pytest"):
        self.framework = framework

    def get_system_prompt(self, context: SkillContext) -> str:
        return f"""You are an expert software engineer writing tests.

## Test Framework
{self.framework}

## Test Requirements
1. Write comprehensive tests covering:
   - Happy path scenarios
   - Edge cases
   - Error conditions
2. Use descriptive test names
3. Include docstrings explaining what each test validates
4. Use fixtures appropriately
5. Mock external dependencies

## Output Format
Provide complete, runnable test code.
"""

    def get_user_prompt(self, context: SkillContext) -> str:
        code = context.config.get("code", "")
        return f"""Write comprehensive tests for this code:

```python
{code}
```

Provide complete test code using {self.framework}."""

    async def execute(self, context: SkillContext, inference_client) -> SkillResult:
        """Execute test generation."""
        system_prompt = self.get_system_prompt(context)
        user_prompt = self.get_user_prompt(context)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        result = await inference_client.chat(messages)
        parsed = self.parse_output(result.text)

        artifacts = {}
        for block in parsed.get("code_blocks", []):
            if block["language"] == "python":
                artifacts["test_generated.py"] = block["code"]
                break

        return SkillResult(
            success=True,
            output=parsed,
            artifacts=artifacts,
            next_steps=["Run tests", "Check coverage"],
        )
