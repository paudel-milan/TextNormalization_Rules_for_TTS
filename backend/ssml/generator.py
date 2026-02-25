"""
SSML Generator
Generates Speech Synthesis Markup Language output for TTS engines.

Supported category tags:
  currency     → <say-as interpret-as="currency">
  cardinal     → <say-as interpret-as="cardinal">
  unit         → <say-as interpret-as="unit">
  date         → <say-as interpret-as="date" format="dmy">
  time         → <say-as interpret-as="time" format="hms24">
  ordinal      → <say-as interpret-as="ordinal">
  named_entity → <sub alias="...">
"""


class SSMLGenerator:
    """Generates SSML markup for normalized text tokens."""

    def __init__(self, language='hi-IN'):
        self.ssml_version = '1.1'
        self.language = language

    def generate(self, tokens):
        """
        Generate full SSML document from normalized tokens.

        Args:
            tokens: List of dicts with 'original', 'normalized', 'category'

        Returns:
            Complete SSML string
        """
        ssml_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis"',
            '        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
            '        xsi:schemaLocation="http://www.w3.org/2001/10/synthesis',
            '                            http://www.w3.org/TR/speech-synthesis11/synthesis.xsd"',
            f'        xml:lang="{self.language}">',
        ]

        for token in tokens:
            category = token['category']
            normalized = token['normalized']
            original = token['original']

            if category == 'currency':
                ssml_parts.append(f'  <say-as interpret-as="currency" format="long">')
                ssml_parts.append(f'    <emphasis level="moderate">{normalized}</emphasis>')
                ssml_parts.append(f'  </say-as>')
            elif category == 'cardinal':
                ssml_parts.append(f'  <say-as interpret-as="cardinal">')
                ssml_parts.append(f'    {normalized}')
                ssml_parts.append(f'  </say-as>')
            elif category == 'unit':
                ssml_parts.append(f'  <say-as interpret-as="unit">')
                ssml_parts.append(f'    {normalized}')
                ssml_parts.append(f'  </say-as>')
            elif category == 'date':
                ssml_parts.append(f'  <say-as interpret-as="date" format="dmy">')
                ssml_parts.append(f'    {normalized}')
                ssml_parts.append(f'  </say-as>')
            elif category == 'time':
                ssml_parts.append(f'  <say-as interpret-as="time" format="hms24">')
                ssml_parts.append(f'    {normalized}')
                ssml_parts.append(f'  </say-as>')
            elif category == 'ordinal':
                ssml_parts.append(f'  <say-as interpret-as="ordinal">')
                ssml_parts.append(f'    {normalized}')
                ssml_parts.append(f'  </say-as>')
            elif category == 'named_entity':
                ssml_parts.append(f'  <sub alias="{normalized}">{original}</sub>')
            else:
                ssml_parts.append(f'  {normalized}')

        ssml_parts.append('</speak>')
        return '\n'.join(ssml_parts)

    def generate_inline(self, tokens):
        """Generate inline SSML (no XML declaration), for embedding in larger documents."""
        parts = []
        for token in tokens:
            category = token['category']
            normalized = token['normalized']
            original = token['original']

            if category == 'currency':
                parts.append(f'<say-as interpret-as="currency">{normalized}</say-as>')
            elif category == 'cardinal':
                parts.append(f'<say-as interpret-as="cardinal">{normalized}</say-as>')
            elif category == 'unit':
                parts.append(f'<say-as interpret-as="unit">{normalized}</say-as>')
            elif category == 'date':
                parts.append(f'<say-as interpret-as="date" format="dmy">{normalized}</say-as>')
            elif category == 'time':
                parts.append(f'<say-as interpret-as="time">{normalized}</say-as>')
            elif category == 'ordinal':
                parts.append(f'<say-as interpret-as="ordinal">{normalized}</say-as>')
            elif category == 'named_entity':
                parts.append(f'<sub alias="{normalized}">{original}</sub>')
            else:
                parts.append(normalized)

        return ' '.join(parts)
