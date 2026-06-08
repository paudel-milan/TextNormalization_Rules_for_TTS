"""
Rule Engine Package
Wraps existing DFA classes for use in the hybrid detection pipeline.
"""

from .detector import RuleBasedDetector

__all__ = ['RuleBasedDetector']
