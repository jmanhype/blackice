"""
Greenfield Skill
================

Generate code from scratch based on a specification.
"""

from dataclasses import dataclass
from typing import Any

from .base import Skill, SkillContext, SkillResult, registry


@registry.register
class GreenfieldSkill(Skill):
    """
    Generate code from a specification.

    This skill takes a spec and produces implementation code.
    """

    name = "greenfield"
    description = "Generate code from a specification"
    required_tools = ["write_file", "read_file"]

    def get_system_prompt(self, context: SkillContext) -> str:
        spec = context.spec

        return f"""You are an expert software engineer implementing code from a specification.

## Specification
Name: {spec.name}
Version: {spec.version}
Description: {spec.description}

## Classes to Implement
{self._format_classes(spec.classes)}

## Functions to Implement
{self._format_functions(spec.functions)}

## Requirements
- Write clean, well-documented code
- Include type hints for all functions
- Follow PEP 8 style guidelines
- Include docstrings for all public functions and classes
- Handle errors appropriately

## Output Format
Provide complete, working code. Use code blocks with the language specified.
"""

    def get_user_prompt(self, context: SkillContext) -> str:
        return f"Implement the {context.spec.name} specification. Start with the core classes and functions."

    async def execute(self, context: SkillContext, inference_client) -> SkillResult:
        """Execute greenfield code generation."""
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
            next_steps=["Run syntax validation", "Run type checking", "Run tests"],
        )

    def _format_classes(self, classes: list[dict]) -> str:
        if not classes:
            return "None specified"

        lines = []
        for cls in classes:
            lines.append(f"- {cls.get('name', 'Unknown')}")
            if cls.get("description"):
                lines.append(f"  Description: {cls['description']}")
            if cls.get("methods"):
                lines.append(f"  Methods: {', '.join(cls['methods'])}")
            if cls.get("attributes"):
                lines.append(f"  Attributes: {', '.join(cls['attributes'])}")

        return "\n".join(lines)

    def _format_functions(self, functions: list[dict]) -> str:
        if not functions:
            return "None specified"

        lines = []
        for func in functions:
            sig = func.get("name", "unknown")
            if func.get("parameters"):
                params = ", ".join(func["parameters"])
                sig = f"{sig}({params})"
            if func.get("return_type"):
                sig = f"{sig} -> {func['return_type']}"

            lines.append(f"- {sig}")
            if func.get("description"):
                lines.append(f"  Description: {func['description']}")

        return "\n".join(lines)
