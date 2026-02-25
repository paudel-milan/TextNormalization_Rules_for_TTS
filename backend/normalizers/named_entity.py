"""
Named Entity Normalizer
Expands known abbreviations and titles (डॉ. → डॉक्टर).
"""


class NamedEntityNormalizer:

    def __init__(self, resources):
        ne_res = resources.get('named_entities', {})
        self.abbreviations = ne_res.get('abbreviations', {})

    def normalize(self, text):
        """डॉ. → डॉक्टर"""
        return self.abbreviations.get(text, text)
