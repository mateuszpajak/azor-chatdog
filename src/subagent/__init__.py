"""
Subagent module initialization
Exports the Subagent class and subagent factory functions.
"""

from .subagent import Subagent
from .snoppy import create_snoppy_subagent

__all__ = ['Subagent', 'create_snoppy_subagent']
