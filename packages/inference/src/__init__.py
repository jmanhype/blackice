"""
BLACKICE Inference
==================

Local LLM inference via vLLM for code generation.
Designed for GPU deployment (3090, 4090, etc.)
"""

from .client import InferenceClient, get_client
from .prompts import PromptTemplate, CodeGenPrompt

__version__ = "0.1.0"
__all__ = [
    "InferenceClient",
    "get_client",
    "PromptTemplate",
    "CodeGenPrompt",
]
