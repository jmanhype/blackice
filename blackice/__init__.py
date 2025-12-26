"""
BLACKICE
========

Neuro-symbolic software factory for greenfield and brownfield code generation.

Usage:
    blackice generate --spec spec.yaml
    blackice extract --path ./existing-code
    blackice run --mode hybrid

Architecture:
    - Inference: vLLM-powered local code generation
    - Extraction: Tree-sitter based brownfield analysis
    - Validation: Neuro-symbolic gates (syntax, types, tests, patterns)
    - Orchestration: Flywheel (generate -> test -> fix -> repeat)
    - Skills: Context-engineered agent capabilities
    - MCP: Model Context Protocol server integration
"""

__version__ = "0.1.0"
__all__ = ["__version__"]
