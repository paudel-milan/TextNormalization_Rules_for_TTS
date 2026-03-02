"""
Number-to-Words Converter
Core utility for converting integers to Hindi/Nepali spoken-form words
using the Indian numbering system (ones, tens, hundreds, thousands, lakhs, crores).
"""


class NumberToWordsConverter:
    """
    Converts numbers to spoken words using Indian numbering system.
    The word mappings come from the language resource file.
    """

    def __init__(self, resources):
        self.ones = resources['numbers']['ones']
        self.tens = resources['numbers']['tens']
        self.scales = resources['numbers']['scales']

    def convert(self, number):
        """Convert an integer to its spoken-word representation."""
        if number == 0:
            return self.ones['0']
        if number < 0:
            return 'माइनस ' + self.convert(-number)
        if number < 100:
            return self._below_hundred(number)
        if number < 1000:
            return self._hundreds(number)
        return self._indian_system(number)

    # ── Internal helpers ──────────────────────────────────────────

    def _below_hundred(self, num):
        if num < 10:
            return self.ones[str(num)]
        if num < 20:
            return self.tens[str(num)]
        tens_digit = (num // 10) * 10
        ones_digit = num % 10
        if ones_digit == 0:
            return self.tens[str(tens_digit)]
        if str(num) in self.tens:
            return self.tens[str(num)]
        return self.tens[str(tens_digit)] + ' ' + self.ones[str(ones_digit)]

    def _hundreds(self, num):
        hundreds_digit = num // 100
        remainder = num % 100
        result = self.ones[str(hundreds_digit)] + ' ' + self.scales['hundred']
        if remainder > 0:
            result += ' ' + self._below_hundred(remainder)
        return result

    def _indian_system(self, num):
        """Crore → Lakh → Thousand → Hundred → Tens/Ones."""
        if num >= 10_000_000:
            crores = num // 10_000_000
            remainder = num % 10_000_000
            result = self.convert(crores) + ' ' + self.scales['crore']
            if remainder > 0:
                result += ' ' + self.convert(remainder)
            return result
        if num >= 100_000:
            lakhs = num // 100_000
            remainder = num % 100_000
            result = self.convert(lakhs) + ' ' + self.scales['lakh']
            if remainder > 0:
                result += ' ' + self.convert(remainder)
            return result
        if num >= 1_000:
            thousands = num // 1_000
            remainder = num % 1_000
            result = self.convert(thousands) + ' ' + self.scales['thousand']
            if remainder > 0:
                result += ' ' + self.convert(remainder)
            return result
        return str(num)
