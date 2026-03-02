"""
Currency Normalizer
Converts currency amounts (₹500, ₹500.50) to spoken Hindi/Nepali form.
"""

import re
from .number_converter import NumberToWordsConverter


class CurrencyNormalizer:

    def __init__(self, resources):
        self.converter = NumberToWordsConverter(resources)
        self.currency_units = resources['currency']

    def normalize(self, text):
        """₹500.50 → पाँच सौ रुपये पचास पैसे"""
        amount_text = re.sub(r'^[₹रुRsINR.\s]+', '', text)
        amount_text = amount_text.replace(',', '')  # handle 1,00,000

        if '.' in amount_text:
            parts = amount_text.split('.')
            rupees = int(parts[0])
            paise = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        else:
            rupees = int(amount_text)
            paise = 0

        result = self.converter.convert(rupees)
        unit_key = 'singular' if rupees == 1 else 'plural'
        result += ' ' + self.currency_units['main_unit'][unit_key]

        if paise > 0:
            result += ' ' + self.converter.convert(paise)
            sub_key = 'singular' if paise == 1 else 'plural'
            result += ' ' + self.currency_units['sub_unit'][sub_key]

        return result
