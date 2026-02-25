"""
Currency DFA — detects currency patterns like ₹500, ₹500.50, Rs. 100.
"""

import re
from .base import BaseDFA


class CurrencyDFA(BaseDFA):
    """
    DFA for detecting currency patterns in Hindi/Nepali text.

    Patterns recognised:
        ₹500, ₹500.50, रु500, Rs. 500, INR 500, ₹1,00,000

    State Machine:
        START → CURRENCY_SYMBOL → INTEGER_PART → [DECIMAL_POINT → DECIMAL_PART] → END
    """

    def __init__(self):
        super().__init__()
        self.states = [
            'START', 'CURRENCY_SYMBOL', 'INTEGER_PART',
            'DECIMAL_POINT', 'DECIMAL_PART', 'END',
        ]
        self.currency_symbols = ['₹', 'रु', 'Rs', 'Rs.', 'INR']

    def match(self, text):
        states_traversed = ['START']

        # Normalize: strip commas so ₹1,00,000 works like ₹100000
        clean = text.replace(',', '')

        # Pattern 1: ₹500 or ₹500.50
        pattern1 = r'^[₹रु]|^Rs\.?|^INR'
        if re.match(pattern1, clean):
            states_traversed.append('CURRENCY_SYMBOL')
            number_part = re.sub(r'^[₹रुRsINR.]+\s*', '', clean)

            if re.match(r'^\d+', number_part):
                states_traversed.append('INTEGER_PART')
                if '.' in number_part:
                    parts = number_part.split('.')
                    if len(parts) == 2 and parts[1].isdigit():
                        states_traversed.append('DECIMAL_POINT')
                        states_traversed.append('DECIMAL_PART')
                states_traversed.append('END')
                return {'matched': True, 'states': states_traversed}

        # Pattern 2: standalone number (e.g. "500" when currency category is active)
        if re.match(r'^\d+\.?\d*$', clean):
            states_traversed.append('INTEGER_PART')
            if '.' in clean:
                states_traversed.append('DECIMAL_POINT')
                states_traversed.append('DECIMAL_PART')
            states_traversed.append('END')
            return {'matched': True, 'states': states_traversed}

        return {'matched': False, 'states': states_traversed}
