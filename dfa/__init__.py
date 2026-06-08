"""
DFA (Deterministic Finite Automaton) Package
Provides state machines for pattern detection across all normalization categories.
"""

from .base import BaseDFA
from .currency import CurrencyDFA
from .cardinal import CardinalDFA
from .unit import UnitDFA
from .date import DateDFA
from .time import TimeDFA
from .ordinal import OrdinalDFA
from .named_entity import NamedEntityDFA

__all__ = [
    'BaseDFA',
    'CurrencyDFA',
    'CardinalDFA',
    'UnitDFA',
    'DateDFA',
    'TimeDFA',
    'OrdinalDFA',
    'NamedEntityDFA',
]
