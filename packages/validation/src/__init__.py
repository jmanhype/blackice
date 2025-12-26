"""
BLACKICE Validation
===================

Quality gates and neuro-symbolic validation.

Combines:
- Static analysis (syntax, types)
- Solver-based verification (BFS, CP-SAT)
- LLM-based review
- Pattern matching (for brownfield)
"""

from .gates import Gate, GateRunner, SyntaxGate, TypeGate, TestGate, PatternGate
from .solvers import BFSSolver, CPSATSolver
from .validators import Validator, ValidationPipeline

__version__ = "0.1.0"
__all__ = [
    # Gates
    "Gate",
    "GateRunner",
    "SyntaxGate",
    "TypeGate",
    "TestGate",
    "PatternGate",
    # Solvers
    "BFSSolver",
    "CPSATSolver",
    # Validators
    "Validator",
    "ValidationPipeline",
]
