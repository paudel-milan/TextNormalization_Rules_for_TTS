"""
Cardinal Normalizer
Converts cardinal numbers (123) to spoken Hindi/Nepali form.
"""

from .number_converter import NumberToWordsConverter


class CardinalNormalizer:

    def __init__(self, resources):
        self.converter = NumberToWordsConverter(resources)

    def normalize(self, text):
        """123 → एक सौ तेईस"""
        return self.converter.convert(int(text))
