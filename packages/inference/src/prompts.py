"""
Prompt Templates
================

Structured prompts for code generation.
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from abc import ABC, abstractmethod


@dataclass
class PromptTemplate(ABC):
    """Base class for prompt templates."""

    @abstractmethod
    def render(self) -> str:
        """Render the prompt to a string."""
        pass

    def to_messages(self) -> list[dict[str, str]]:
        """Convert to chat messages format."""
        return [{"role": "user", "content": self.render()}]


@dataclass
class CodeGenPrompt(PromptTemplate):
    """
    Prompt for code generation.

    Designed for DeepSeek Coder and similar models.
    """
    task: str
    language: str = "python"
    context: Optional[str] = None
    constraints: list[str] = field(default_factory=list)
    examples: list[dict[str, str]] = field(default_factory=list)
    output_format: str = "code"  # code, json, markdown

    def render(self) -> str:
        parts = []

        # System context
        parts.append(f"You are an expert {self.language} developer.")

        # Context
        if self.context:
            parts.append(f"\n## Context\n{self.context}")

        # Task
        parts.append(f"\n## Task\n{self.task}")

        # Constraints
        if self.constraints:
            parts.append("\n## Requirements")
            for c in self.constraints:
                parts.append(f"- {c}")

        # Examples
        if self.examples:
            parts.append("\n## Examples")
            for ex in self.examples:
                parts.append(f"\nInput: {ex.get('input', '')}")
                parts.append(f"Output: {ex.get('output', '')}")

        # Output format
        if self.output_format == "code":
            parts.append(f"\nRespond with only the {self.language} code, no explanations.")
        elif self.output_format == "json":
            parts.append("\nRespond with valid JSON only.")

        return "\n".join(parts)


@dataclass
class ExtractionPrompt(PromptTemplate):
    """
    Prompt for brownfield code analysis.
    """
    code: str
    language: str = "python"
    extract_what: str = "patterns"  # patterns, types, architecture, all

    def render(self) -> str:
        parts = [
            f"Analyze this {self.language} code and extract {self.extract_what}.",
            "",
            "```" + self.language,
            self.code,
            "```",
            "",
        ]

        if self.extract_what == "patterns":
            parts.append("""Extract:
1. Error handling patterns (try/except, result types, etc.)
2. Logging patterns
3. Dependency injection patterns
4. State management patterns

Respond in JSON format:
{
  "patterns": {
    "error_handling": "description",
    "logging": "description",
    "dependency_injection": "description",
    "state_management": "description"
  }
}""")

        elif self.extract_what == "types":
            parts.append("""Extract all type definitions including:
1. Classes and their attributes
2. Function signatures
3. Type aliases
4. Enums

Respond in JSON format.""")

        elif self.extract_what == "architecture":
            parts.append("""Identify the architectural pattern:
1. Layered (presentation, business, data)
2. Hexagonal (ports and adapters)
3. Clean architecture
4. Microservices
5. Monolithic
6. Other

Respond in JSON format:
{
  "architecture": "pattern_name",
  "layers": ["layer1", "layer2"],
  "key_abstractions": ["abstraction1", "abstraction2"]
}""")

        return "\n".join(parts)


@dataclass
class CompatibilityPrompt(PromptTemplate):
    """
    Prompt for brownfield compatibility checking.
    """
    existing_code: str
    new_code: str
    language: str = "python"

    def render(self) -> str:
        return f"""Compare these two {self.language} code samples for compatibility.

## Existing Code (to match)
```{self.language}
{self.existing_code}
```

## New Code (to check)
```{self.language}
{self.new_code}
```

Check for:
1. Naming convention consistency (snake_case, camelCase, etc.)
2. Error handling pattern consistency
3. Import style consistency
4. Documentation style consistency
5. Code structure consistency

Respond in JSON:
{{
  "compatible": true/false,
  "score": 0.0-1.0,
  "issues": ["issue1", "issue2"],
  "suggestions": ["suggestion1", "suggestion2"]
}}"""


@dataclass
class RefactorPrompt(PromptTemplate):
    """
    Prompt for code refactoring.
    """
    code: str
    language: str = "python"
    target_patterns: dict[str, str] = field(default_factory=dict)
    keep_behavior: bool = True

    def render(self) -> str:
        parts = [
            f"Refactor this {self.language} code to match the specified patterns.",
            "",
            "## Original Code",
            "```" + self.language,
            self.code,
            "```",
            "",
        ]

        if self.target_patterns:
            parts.append("## Target Patterns")
            for name, pattern in self.target_patterns.items():
                parts.append(f"- {name}: {pattern}")

        if self.keep_behavior:
            parts.append("\nIMPORTANT: Preserve the exact behavior of the original code.")

        parts.append(f"\nRespond with only the refactored {self.language} code.")

        return "\n".join(parts)


@dataclass
class TestGenPrompt(PromptTemplate):
    """
    Prompt for test generation.
    """
    code: str
    language: str = "python"
    test_framework: str = "pytest"
    coverage_target: str = "high"  # minimal, medium, high, exhaustive

    def render(self) -> str:
        coverage_desc = {
            "minimal": "basic happy path tests",
            "medium": "happy path and common error cases",
            "high": "comprehensive coverage including edge cases",
            "exhaustive": "all possible paths and edge cases",
        }

        return f"""Generate {self.test_framework} tests for this {self.language} code.

## Code to Test
```{self.language}
{self.code}
```

## Requirements
- Use {self.test_framework} framework
- Coverage level: {self.coverage_target} ({coverage_desc.get(self.coverage_target, '')})
- Include docstrings for each test
- Use descriptive test names

Respond with only the test code."""
