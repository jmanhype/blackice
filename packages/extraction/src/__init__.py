"""
BLACKICE Extraction
===================

Brownfield code analysis and spec extraction.

Uses tree-sitter for AST parsing and LLMs for semantic understanding.
"""

from .extractor import CodeExtractor, extract_spec
from .patterns import PatternDetector, Pattern
from .languages import LanguageSupport, get_language_support

__version__ = "0.1.0"
__all__ = [
    "CodeExtractor",
    "extract_spec",
    "PatternDetector",
    "Pattern",
    "LanguageSupport",
    "get_language_support",
]
