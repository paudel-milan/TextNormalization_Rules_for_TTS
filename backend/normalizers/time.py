"""
Time Normalizer
Converts time expressions (10:30, 14:45, 10:30 AM) to spoken form.
"""

import re
from .number_converter import NumberToWordsConverter


class TimeNormalizer:

    def __init__(self, resources):
        self.converter = NumberToWordsConverter(resources)
        self.time_res = resources.get('time', {})

    def normalize(self, text, hour=None, minute=None, second=None, period=None):
        """10:30 → दस बजकर तीस मिनट"""
        if not (hour and minute):
            m = re.match(r'(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(AM|PM)?', text, re.IGNORECASE)
            if not m:
                return text
            hour, minute = m.group(1), m.group(2)
            second = m.group(3)
            period = m.group(4)

        hour_int = int(hour)
        minute_int = int(minute)
        second_int = int(second) if second else None

        # Period prefix: सुबह / दोपहर / शाम / रात
        period_prefix = ''
        if period:
            p = period.upper().replace('.', '')
            if p == 'AM':
                period_prefix = self.time_res.get('periods', {}).get('AM', 'सुबह')
            else:
                if hour_int < 4 or hour_int == 12:
                    period_prefix = self.time_res.get('periods', {}).get('PM_afternoon', 'दोपहर')
                elif hour_int < 7:
                    period_prefix = self.time_res.get('periods', {}).get('PM_evening', 'शाम')
                else:
                    period_prefix = self.time_res.get('periods', {}).get('PM_night', 'रात')

        hour_words = self.converter.convert(hour_int)

        if minute_int == 0 and second_int is None:
            result = f"{hour_words} {self.time_res.get('hour_marker', 'बजे')}"
        else:
            minute_words = self.converter.convert(minute_int)
            connector = self.time_res.get('hour_minute_connector', 'बजकर')
            minute_unit = self.time_res.get('minute_word', 'मिनट')
            result = f"{hour_words} {connector} {minute_words} {minute_unit}"

        if second_int is not None and second_int > 0:
            second_words = self.converter.convert(second_int)
            second_unit = self.time_res.get('second_word', 'सेकंड')
            result += f" {second_words} {second_unit}"

        if period_prefix:
            result = f"{period_prefix} {result}"

        return result
