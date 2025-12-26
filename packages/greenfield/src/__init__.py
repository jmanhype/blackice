"""
BLACKICE Greenfield
===================

Integration with Sean Chatman's ontology-to-code stack:
- ggen: Ontology → Code generation
- unrdf: RDF Knowledge Graph Platform
- gitvan: Git workflow automation
- KNHK: Knowledge graph hooks

This provides DETERMINISTIC code generation from ontologies,
not probabilistic LLM output.
"""

from .ggen_adapter import GgenAdapter
from .unrdf_adapter import UnrdfAdapter
from .gitvan_adapter import GitvanAdapter

__version__ = "0.1.0"
__all__ = [
    "GgenAdapter",
    "UnrdfAdapter",
    "GitvanAdapter",
]
