"""
Rule-Based Detector — wraps existing DFA classes for the hybrid pipeline.

Provides a unified interface to run ALL DFAs against a single token
and return the detected category with confidence.
"""

import json
from pathlib import Path

import sys
# Ensure the backend package root is importable
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from dfa import (
    CurrencyDFA, CardinalDFA,
    UnitDFA, DateDFA, TimeDFA, OrdinalDFA, NamedEntityDFA,
)


class RuleBasedDetector:
    """
    Wraps existing DFA classes for rule-based category detection.

    Runs all DFAs against a single token in priority order and
    returns the first match. This mirrors the priority logic in
    NormalizationEngine but operates on individual tokens.
    """

    # Detection priority (highest first), same as NormalizationEngine
    PRIORITY_ORDER = [
        'date', 'time', 'currency', 'unit',
        'ordinal', 'named_entity', 'cardinal',
    ]

    def __init__(self, language='hi-IN'):
        self.language = language
        self.resources = self._load_resources()
        self.dfas = self._init_dfas()

    def _load_resources(self):
        """Load language resources for DFA initialization."""
        resource_path = _BACKEND_DIR / 'resources' / f'{self.language}.json'
        with open(resource_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _init_dfas(self):
        """Initialize all DFA instances from existing classes."""
        patterns = self.resources.get('patterns', {})

        dfas = {}

        # Currency
        dfas['currency'] = CurrencyDFA(patterns={
            'currency_symbol': patterns.get('currency_symbol'),
            'currency_strip': patterns.get('currency_strip'),
        })

        # Cardinal
        dfas['cardinal'] = CardinalDFA(pattern=patterns.get('cardinal'))

        # Unit
        dfas['unit'] = UnitDFA(pattern=patterns.get('unit'))

        # Date
        dfas['date'] = DateDFA(pattern=patterns.get('date'))

        # Time
        dfas['time'] = TimeDFA(pattern=patterns.get('time'))

        # Ordinal
        dfas['ordinal'] = OrdinalDFA(pattern=patterns.get('ordinal'))

        # Named Entity
        ne_keys = list(
            self.resources.get('named_entities', {}).get('abbreviations', {}).keys()
        )
        dfas['named_entity'] = NamedEntityDFA(known_entities=ne_keys)

        return dfas

    def detect(self, token):
        """
        Run all DFAs against a single token in priority order.

        Args:
            token: The token string to check

        Returns:
            dict with:
                'category':   str  — detected category or 'text'
                'confidence':  float — rule confidence (0.9 for match, 0.0 for no match)
                'dfa_states': list  — state transitions from matching DFA
                'match_data':  dict — raw DFA match result
        """
        for category in self.PRIORITY_ORDER:
            dfa = self.dfas.get(category)
            if dfa is None:
                continue

            try:
                result = dfa.match(token)
                if result.get('matched', False):
                    return {
                        'category': category,
                        'confidence': 0.9,  # High confidence for rule match
                        'dfa_states': result.get('states', []),
                        'match_data': result,
                    }
            except Exception:
                # DFA raised an error — skip this category
                continue

        return {
            'category': 'text',
            'confidence': 0.0,
            'dfa_states': [],
            'match_data': {},
        }

    def detect_all(self, token):
        """
        Run ALL DFAs against a token (not just first match).

        Returns:
            list of dicts for each matching DFA category
        """
        matches = []
        for category in self.PRIORITY_ORDER:
            dfa = self.dfas.get(category)
            if dfa is None:
                continue

            try:
                result = dfa.match(token)
                if result.get('matched', False):
                    matches.append({
                        'category': category,
                        'confidence': 0.9,
                        'dfa_states': result.get('states', []),
                        'match_data': result,
                    })
            except Exception:
                continue

        return matches
