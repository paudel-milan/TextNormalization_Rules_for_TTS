"""
Unit Normalizer
Converts measurement expressions (5kg, 25°C) to spoken form.
"""

import re
from .number_converter import NumberToWordsConverter


class UnitNormalizer:

    def __init__(self, resources):
        self.converter = NumberToWordsConverter(resources)
        self.unit_map = resources.get('units', {})
        self.patterns = resources.get('patterns', {})
        self.rules = resources.get('rules', {})

    def normalize(self, text, number_str=None, unit_str=None):
        """5kg → पाँच किलोग्राम"""
        if number_str and unit_str:
            num, unit = number_str, unit_str
        else:
            pat = self.patterns.get('unit', r'^(\d+(?:\.\d+)?)\s*(.+)$')
            m = re.match(pat, text)
            if not m:
                return text
            num, unit = m.group(1), m.group(2)

        if '.' in num:
            int_part, dec_part = num.split('.')
            decimal_word = self.rules.get('number', {}).get('decimal_word', 'दशमलव')
            number_words = (
                self.converter.convert(int(int_part))
                + f" {decimal_word} "
                + self.converter.convert(int(dec_part))
            )
        else:
            number_words = self.converter.convert(int(num))

        unit_hindi = self.unit_map.get(unit, unit)
        return f"{number_words} {unit_hindi}"
