"""
BLACKICE Skills
===============

Agent skills for code generation and analysis.

Skills are context engineering patterns that help agents
perform specific tasks effectively.
"""

from .base import Skill, SkillRegistry
from .greenfield import GreenfieldSkill
from .brownfield import BrownfieldSkill
from .refactor import RefactorSkill

__version__ = "0.1.0"
__all__ = [
    "Skill",
    "SkillRegistry",
    "GreenfieldSkill",
    "BrownfieldSkill",
    "RefactorSkill",
]
