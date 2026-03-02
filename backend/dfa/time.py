"""
Time DFA — detects time patterns like 10:30, 14:45, 10:30:15, 10:30AM.
"""

import re
from .base import BaseDFA


class TimeDFA(BaseDFA):
    """
    DFA for detecting time patterns.

    Patterns recognised:
        HH:MM, HH:MM:SS, HH:MMAM/PM, HH:MM AM/PM (separated AM/PM via engine lookahead)

    State Machine:
        START → HOUR → COLON → MINUTE → [COLON → SECOND] → [PERIOD] → END
    """

    def __init__(self):
        super().__init__()
        self.states = ['START', 'HOUR', 'COLON', 'MINUTE', 'COLON', 'SECOND', 'PERIOD', 'END']
        self._pattern = re.compile(
            r'^(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(AM|PM|am|pm|A\.M\.|P\.M\.)?$'
        )

    def match(self, text):
        states_traversed = ['START']
        m = self._pattern.match(text)
        if m:
            hour, minute = int(m.group(1)), int(m.group(2))
            second = int(m.group(3)) if m.group(3) else None
            period = m.group(4)

            if 0 <= hour <= 23 and 0 <= minute <= 59:
                if second is not None and not (0 <= second <= 59):
                    return {'matched': False, 'states': states_traversed}

                states_traversed.extend(['HOUR', 'COLON', 'MINUTE'])
                if second is not None:
                    states_traversed.extend(['COLON', 'SECOND'])
                if period:
                    states_traversed.append('PERIOD')
                states_traversed.append('END')

                return {
                    'matched': True,
                    'states': states_traversed,
                    'hour': str(m.group(1)),
                    'minute': str(m.group(2)),
                    'second': str(m.group(3)) if m.group(3) else None,
                    'period': period.upper().replace('.', '') if period else None,
                }
        return {'matched': False, 'states': states_traversed}
