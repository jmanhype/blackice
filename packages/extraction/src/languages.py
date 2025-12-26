"""
Language Support
================

Language-specific parsing and extraction support.
"""

from dataclasses import dataclass, field
from typing import Optional, Callable, Any
from pathlib import Path


@dataclass
class LanguageSupport:
    """Configuration for a supported language."""
    name: str
    extensions: list[str]
    tree_sitter_module: Optional[str] = None
    comment_styles: list[str] = field(default_factory=list)
    docstring_style: Optional[str] = None
    naming_conventions: dict[str, str] = field(default_factory=dict)


# Language configurations
LANGUAGES = {
    "python": LanguageSupport(
        name="python",
        extensions=[".py", ".pyi"],
        tree_sitter_module="tree_sitter_python",
        comment_styles=["#"],
        docstring_style='"""',
        naming_conventions={
            "classes": "PascalCase",
            "functions": "snake_case",
            "variables": "snake_case",
            "constants": "UPPER_SNAKE_CASE",
        },
    ),
    "javascript": LanguageSupport(
        name="javascript",
        extensions=[".js", ".mjs", ".cjs"],
        tree_sitter_module="tree_sitter_javascript",
        comment_styles=["//", "/*"],
        docstring_style="/**",
        naming_conventions={
            "classes": "PascalCase",
            "functions": "camelCase",
            "variables": "camelCase",
            "constants": "UPPER_SNAKE_CASE",
        },
    ),
    "typescript": LanguageSupport(
        name="typescript",
        extensions=[".ts", ".tsx", ".mts", ".cts"],
        tree_sitter_module="tree_sitter_typescript",
        comment_styles=["//", "/*"],
        docstring_style="/**",
        naming_conventions={
            "classes": "PascalCase",
            "interfaces": "PascalCase",
            "functions": "camelCase",
            "variables": "camelCase",
            "constants": "UPPER_SNAKE_CASE",
        },
    ),
    "rust": LanguageSupport(
        name="rust",
        extensions=[".rs"],
        tree_sitter_module="tree_sitter_rust",
        comment_styles=["//", "/*"],
        docstring_style="///",
        naming_conventions={
            "structs": "PascalCase",
            "traits": "PascalCase",
            "functions": "snake_case",
            "variables": "snake_case",
            "constants": "UPPER_SNAKE_CASE",
        },
    ),
    "go": LanguageSupport(
        name="go",
        extensions=[".go"],
        tree_sitter_module="tree_sitter_go",
        comment_styles=["//", "/*"],
        docstring_style="//",
        naming_conventions={
            "types": "PascalCase",
            "functions": "camelCase",
            "variables": "camelCase",
            "constants": "camelCase",
            "exported": "PascalCase",
        },
    ),
}


def get_language_support(language: str) -> Optional[LanguageSupport]:
    """Get language support configuration."""
    return LANGUAGES.get(language.lower())


def detect_language(path: Path) -> Optional[str]:
    """Detect language from file extension."""
    ext = path.suffix.lower()
    for lang, support in LANGUAGES.items():
        if ext in support.extensions:
            return lang
    return None


def get_supported_languages() -> list[str]:
    """Get list of supported languages."""
    return list(LANGUAGES.keys())


def get_file_extensions(language: str) -> list[str]:
    """Get file extensions for a language."""
    support = get_language_support(language)
    return support.extensions if support else []
