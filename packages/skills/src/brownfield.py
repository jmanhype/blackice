"""
Brownfield Skill
================

Generate code that integrates with existing codebase.
"""

from dataclasses import dataclass
from typing import Any

from .base import Skill, SkillContext, SkillResult, registry


@registry.register
class BrownfieldSkill(Skill):
    """
    Generate code compatible with existing codebase.

    This skill:
    1. Analyzes existing patterns
    2. Generates code that matches those patterns
    3. Ensures compatibility with existing code
    """

    name = "brownfield"
    description = "Generate code compatible with existing codebase"
    required_tools = ["read_file", "write_file", "list_files", "git_info"]

    def get_system_prompt(self, context: SkillContext) -> str:
        spec = context.spec
        patterns = spec.patterns or {}
        naming = spec.naming_conventions or {}

        return f"""You are an expert software engineer adding to an existing codebase.

## Existing Codebase Patterns

### Naming Conventions
{self._format_naming(naming)}

### Code Patterns
{self._format_patterns(patterns)}

### Architectural Style
{spec.architectural_style or "Not specified"}

## New Code Requirements
Name: {spec.name}
Version: {spec.version}
Description: {spec.description}

## Critical Requirements
1. MATCH existing naming conventions exactly
2. FOLLOW existing patterns for error handling, logging, etc.
3. MAINTAIN architectural consistency
4. USE existing utilities and helpers where available
5. WRITE code that looks like it belongs in this codebase

## Output Format
Provide complete code that seamlessly integrates with the existing codebase.
"""

    def get_user_prompt(self, context: SkillContext) -> str:
        return f"""Implement {context.spec.name} in a way that integrates seamlessly with the existing codebase.

The code should:
- Follow the same patterns as existing code
- Use the same naming conventions
- Handle errors the same way
- Log in the same format

Start with the implementation."""

    async def execute(self, context: SkillContext, inference_client) -> SkillResult:
        """Execute brownfield code generation."""
        # First, analyze existing code if path provided
        if context.spec.extracted_from:
            # Load additional context from extraction
            context.config["extraction_path"] = str(context.spec.extracted_from)

        system_prompt = self.get_system_prompt(context)
        user_prompt = self.get_user_prompt(context)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        result = await inference_client.chat(messages)
        parsed = self.parse_output(result.text)

        # Extract code files
        artifacts = {}
        for i, block in enumerate(parsed.get("code_blocks", [])):
            if block["language"] == "python":
                filename = f"generated_{i}.py" if i > 0 else "main.py"
                artifacts[filename] = block["code"]

        return SkillResult(
            success=True,
            output=parsed,
            artifacts=artifacts,
            next_steps=[
                "Validate pattern compatibility",
                "Run syntax validation",
                "Run integration tests",
            ],
        )

    def _format_naming(self, naming: dict[str, str]) -> str:
        if not naming:
            return "Not specified - infer from context"

        lines = []
        for element, convention in naming.items():
            lines.append(f"- {element}: {convention}")
        return "\n".join(lines)

    def _format_patterns(self, patterns: dict[str, Any]) -> str:
        if not patterns:
            return "Not specified - infer from context"

        lines = []
        for pattern, value in patterns.items():
            if isinstance(value, dict):
                lines.append(f"- {pattern}:")
                for k, v in value.items():
                    lines.append(f"    {k}: {v}")
            else:
                lines.append(f"- {pattern}: {value}")
        return "\n".join(lines)
