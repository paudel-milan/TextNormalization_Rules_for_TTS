"""
Core Normalization Engine
Orchestrates DFA-based detection and rule-based normalization for all categories.

Detection priority (highest first):
  date → time → currency → unit → ordinal → named_entity → cardinal

This ordering ensures multi-character patterns like dates (15/08/2024) aren't
mistakenly consumed by simpler DFAs like cardinal.
"""

import json
from pathlib import Path

from dfa import (
    CurrencyDFA, CardinalDFA,
    UnitDFA, DateDFA, TimeDFA, OrdinalDFA, NamedEntityDFA,
)
from normalizers import (
    CurrencyNormalizer, CardinalNormalizer,
    UnitNormalizer, DateNormalizer, TimeNormalizer,
    OrdinalNormalizer, NamedEntityNormalizer,
)
from ssml import SSMLGenerator


class NormalizationEngine:
    """
    Main engine that coordinates:
    1. DFA-based token detection
    2. Rule-based normalization
    3. SSML generation
    """

    # Root directory of the backend package (parent of engine/)
    _BACKEND_DIR = Path(__file__).resolve().parent.parent

    def __init__(self, language='hi-IN'):
        self.language = language
        self.resources = self._load_language_resources()

        # ── DFAs ──────────────────────────────────────────────────
        self.currency_dfa = CurrencyDFA()
        self.cardinal_dfa = CardinalDFA()
        self.unit_dfa = UnitDFA()
        self.date_dfa = DateDFA()
        self.time_dfa = TimeDFA()
        self.ordinal_dfa = OrdinalDFA()

        ne_keys = list(
            self.resources.get('named_entities', {}).get('abbreviations', {}).keys()
        )
        self.named_entity_dfa = NamedEntityDFA(known_entities=ne_keys)

        # ── Normalizers ───────────────────────────────────────────
        self.currency_normalizer = CurrencyNormalizer(self.resources)
        self.cardinal_normalizer = CardinalNormalizer(self.resources)
        self.unit_normalizer = UnitNormalizer(self.resources)
        self.date_normalizer = DateNormalizer(self.resources)
        self.time_normalizer = TimeNormalizer(self.resources)
        self.ordinal_normalizer = OrdinalNormalizer(self.resources)
        self.named_entity_normalizer = NamedEntityNormalizer(self.resources)

        # ── SSML generator ────────────────────────────────────────
        self.ssml_generator = SSMLGenerator(language=self.language)

    def _load_language_resources(self):
        """Load language-specific resources from JSON file."""
        resource_path = self._BACKEND_DIR / 'resources' / f'{self.language}.json'
        with open(resource_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # ──────────────────────────────────────────────────────────────
    #  Main normalisation pipeline
    # ──────────────────────────────────────────────────────────────
    def normalize(self, text, categories):
        """
        Main normalization pipeline.

        Args:
            text:       Input text
            categories: List of categories to apply
                        (e.g. ['currency', 'cardinal', 'date', ...])

        Returns:
            dict with normalized_text, ssml, dfa_info
        """
        tokens = []
        dfa_info = []
        words = text.split()
        i = 0

        while i < len(words):
            word = words[i]
            matched = False

            # ── Priority 1: Date ──────────────────────────────────
            if not matched and 'date' in categories:
                result = self.date_dfa.match(word)
                if result['matched']:
                    normalized = self.date_normalizer.normalize(
                        word,
                        day=result.get('day'),
                        month=result.get('month'),
                        year=result.get('year'),
                    )
                    tokens.append({
                        'original': word, 'normalized': normalized,
                        'category': 'date', 'dfa_states': result['states'],
                    })
                    dfa_info.append({
                        'category': 'date', 'original': word,
                        'states': result['states'],
                    })
                    matched = True

            # ── Priority 2: Time ──────────────────────────────────
            if not matched and 'time' in categories:
                result = self.time_dfa.match(word)
                if result['matched']:
                    period = result.get('period')
                    if not period and i + 1 < len(words):
                        nxt = words[i + 1].upper().replace('.', '')
                        if nxt in ('AM', 'PM'):
                            period = nxt
                            i += 1
                    normalized = self.time_normalizer.normalize(
                        word,
                        hour=result.get('hour'),
                        minute=result.get('minute'),
                        second=result.get('second'),
                        period=period,
                    )
                    tokens.append({
                        'original': word, 'normalized': normalized,
                        'category': 'time', 'dfa_states': result['states'],
                    })
                    dfa_info.append({
                        'category': 'time', 'original': word,
                        'states': result['states'],
                    })
                    matched = True

            # ── Priority 3: Currency ──────────────────────────────
            if not matched and 'currency' in categories:
                result = self.currency_dfa.match(word)
                if result['matched']:
                    normalized = self.currency_normalizer.normalize(word)
                    tokens.append({
                        'original': word, 'normalized': normalized,
                        'category': 'currency', 'dfa_states': result['states'],
                    })
                    dfa_info.append({
                        'category': 'currency', 'original': word,
                        'states': result['states'],
                    })
                    matched = True

            # ── Priority 4: Unit ──────────────────────────────────
            if not matched and 'unit' in categories:
                result = self.unit_dfa.match(word)
                if result['matched']:
                    normalized = self.unit_normalizer.normalize(
                        word,
                        number_str=result.get('number'),
                        unit_str=result.get('unit'),
                    )
                    tokens.append({
                        'original': word, 'normalized': normalized,
                        'category': 'unit', 'dfa_states': result['states'],
                    })
                    dfa_info.append({
                        'category': 'unit', 'original': word,
                        'states': result['states'],
                    })
                    matched = True

            # ── Priority 5: Ordinal ───────────────────────────────
            if not matched and 'ordinal' in categories:
                result = self.ordinal_dfa.match(word)
                if result['matched']:
                    normalized = self.ordinal_normalizer.normalize(
                        word, number_str=result.get('number'),
                    )
                    tokens.append({
                        'original': word, 'normalized': normalized,
                        'category': 'ordinal', 'dfa_states': result['states'],
                    })
                    dfa_info.append({
                        'category': 'ordinal', 'original': word,
                        'states': result['states'],
                    })
                    matched = True

            # ── Priority 6: Named Entity ──────────────────────────
            if not matched and 'named_entity' in categories:
                result = self.named_entity_dfa.match(word)
                if result['matched']:
                    normalized = self.named_entity_normalizer.normalize(word)
                    tokens.append({
                        'original': word, 'normalized': normalized,
                        'category': 'named_entity', 'dfa_states': result['states'],
                    })
                    dfa_info.append({
                        'category': 'named_entity', 'original': word,
                        'states': result['states'],
                    })
                    matched = True

            # ── Priority 7: Cardinal (lowest) ─────────────────────
            if not matched and 'cardinal' in categories:
                result = self.cardinal_dfa.match(word)
                if result['matched']:
                    normalized = self.cardinal_normalizer.normalize(word)
                    tokens.append({
                        'original': word, 'normalized': normalized,
                        'category': 'cardinal', 'dfa_states': result['states'],
                    })
                    dfa_info.append({
                        'category': 'cardinal', 'original': word,
                        'states': result['states'],
                    })
                    matched = True

            # ── No match: keep original text ──────────────────────
            if not matched:
                tokens.append({
                    'original': word, 'normalized': word,
                    'category': 'text', 'dfa_states': [],
                })

            i += 1

        normalized_text = ' '.join(t['normalized'] for t in tokens)
        ssml = self.ssml_generator.generate(tokens)

        return {
            'normalized_text': normalized_text,
            'ssml': ssml,
            'dfa_info': dfa_info,
        }
