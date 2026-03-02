"""
Date DFA — detects date patterns like 15/08/2024, 01-01-2025, 26.01.2026.
"""

import re
from .base import BaseDFA


class DateDFA(BaseDFA):
    """
    DFA for detecting date patterns.

    Patterns recognised:
        DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY

    State Machine:
        START → DAY → SEPARATOR → MONTH → SEPARATOR → YEAR → END
    """

    def __init__(self):
        super().__init__()
        self.states = ['START', 'DAY', 'SEPARATOR', 'MONTH', 'SEPARATOR', 'YEAR', 'END']
        self._pattern = re.compile(r'^(\d{1,2})([/\-\.])(\d{1,2})\2(\d{2,4})$')

    def match(self, text):
        states_traversed = ['START']
        m = self._pattern.match(text)
        if m:
            day_int, month_int = int(m.group(1)), int(m.group(3))
            if 1 <= day_int <= 31 and 1 <= month_int <= 12:
                states_traversed.extend([
                    'DAY', 'SEPARATOR', 'MONTH', 'SEPARATOR', 'YEAR', 'END',
                ])
                return {
                    'matched': True,
                    'states': states_traversed,
                    'day': m.group(1),
                    'month': m.group(3),
                    'year': m.group(4),
                }
        return {'matched': False, 'states': states_traversed}
