"""
Date Normalizer
Converts date expressions (15/08/2024) to spoken form.
"""

import re
from .number_converter import NumberToWordsConverter


class DateNormalizer:

    def __init__(self, resources):
        self.converter = NumberToWordsConverter(resources)
        self.months = resources.get('dates', {}).get('months', {})
        self.patterns = resources.get('patterns', {})

    def normalize(self, text, day=None, month=None, year=None):
        """15/08/2024 → पंद्रह अगस्त दो हज़ार चौबीस"""
        if not (day and month and year):
            pat = self.patterns.get('date', r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})')
            m = re.match(pat, text)
            if not m:
                return text
            
            # Extract groups. If the pattern has 4+ groups, it likely captures the separator.
            # standard: (day, month, year)
            # with separator: (day, separator, month, year)
            if m.lastindex >= 4:
                day, month, year = m.group(1), m.group(3), m.group(4)
            else:
                day, month, year = m.group(1), m.group(2), m.group(3)

        day_words = self.converter.convert(int(day))

        month_int = str(int(month))
        month_name = self.months.get(month_int, month)

        year_int = int(year)
        if year_int < 100:
            year_int += 2000
        year_words = self.converter.convert(year_int)

        return f"{day_words} {month_name} {year_words}"
