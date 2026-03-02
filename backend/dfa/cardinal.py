"""
Cardinal DFA — detects pure digit sequences like 123, 5000000.
"""

import re
from .base import BaseDFA


class CardinalDFA(BaseDFA):
    """
    DFA for detecting cardinal numbers.

    Patterns recognised:
        123, 1234, 5000000

    State Machine:
        START → DIGIT → [DIGIT]* → END
    """

    def __init__(self):
        super().__init__()
        self.states = ['START', 'DIGIT', 'END']

    def match(self, text):
        states_traversed = ['START']

        if re.match(r'^\d+$', text):
            states_traversed.append('DIGIT')
            for _ in text[1:]:
                states_traversed.append('DIGIT')
            states_traversed.append('END')
            return {'matched': True, 'states': states_traversed}

        return {'matched': False, 'states': states_traversed}
