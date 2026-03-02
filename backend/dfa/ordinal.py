"""
Ordinal DFA — detects ordinal patterns like 1st, 2nd, 3rd, 5th, 3रा.
"""

import re
from .base import BaseDFA


class OrdinalDFA(BaseDFA):
    """
    DFA for detecting ordinal number patterns.

    Patterns recognised:
        1st, 2nd, 3rd, 4th, 21st, …  (English suffixes)
        1ला, 2रा, 3रा, 5वाँ, …        (Hindi suffixes)

    State Machine:
        START → DIGIT → ORDINAL_SUFFIX → END
    """

    def __init__(self):
        super().__init__()
        self.states = ['START', 'DIGIT', 'ORDINAL_SUFFIX', 'END']
        self._pattern = re.compile(
            r'^(\d+)(st|nd|rd|th|ला|रा|था|वाँ|वां|वीं)$',
            re.IGNORECASE,
        )

    def match(self, text):
        states_traversed = ['START']
        m = self._pattern.match(text)
        if m:
            states_traversed.extend(['DIGIT', 'ORDINAL_SUFFIX', 'END'])
            return {
                'matched': True,
                'states': states_traversed,
                'number': m.group(1),
                'suffix': m.group(2),
            }
        return {'matched': False, 'states': states_traversed}
