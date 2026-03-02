"""
Unit DFA — detects measurement-unit patterns like 5kg, 10km, 25°C, 500MB.
"""

import re
from .base import BaseDFA


class UnitDFA(BaseDFA):
    """
    DFA for detecting measurement unit patterns.

    Patterns recognised:
        5kg, 10km, 100ml, 25°C, 500MB (number glued to unit)

    State Machine:
        START → NUMBER → UNIT_SYMBOL → END
    """

    UNIT_PATTERN = (
        r'(?:kg|g|mg|km|m|cm|mm|mi|ft|in|l|ml|kl'
        r'|°C|°F|K'
        r'|kmph|mph|m/s'
        r'|Hz|kHz|MHz|GHz'
        r'|W|kW|MW|V|A'
        r'|KB|MB|GB|TB'
        r'|किमी|मी|सेमी|किग्रा|ग्रा|ली|मिली)'
    )

    def __init__(self):
        super().__init__()
        self.states = ['START', 'NUMBER', 'UNIT_SYMBOL', 'END']
        self._pattern = re.compile(
            r'^(\d+(?:\.\d+)?)\s*(' + self.UNIT_PATTERN + r')$'
        )

    def match(self, text):
        states_traversed = ['START']
        m = self._pattern.match(text)
        if m:
            states_traversed.extend(['NUMBER', 'UNIT_SYMBOL', 'END'])
            return {
                'matched': True,
                'states': states_traversed,
                'number': m.group(1),
                'unit': m.group(2),
            }
        return {'matched': False, 'states': states_traversed}
