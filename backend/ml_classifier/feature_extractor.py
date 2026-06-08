"""
Feature Extractor for ML-based Token Category Classification.

Extracts numeric, symbolic, contextual, and pattern-based features
from each token and its surrounding context to feed into the ML classifier.
"""

import re
import numpy as np


# Known currency symbols across supported languages
CURRENCY_SYMBOLS = {'₹', '$', '€', '£', '¥', 'रु', 'रू', 'Rs', 'Rs.', 'INR', 'NPR'}

# Known unit suffixes across supported languages
UNIT_SUFFIXES = {
    'kg', 'g', 'mg', 'km', 'm', 'cm', 'mm', 'mi', 'ft', 'in',
    'l', 'ml', 'kl', '°C', '°F', 'K', 'kmph', 'mph', 'm/s',
    'Hz', 'kHz', 'MHz', 'GHz', 'W', 'kW', 'MW', 'V', 'A',
    'KB', 'MB', 'GB', 'TB',
    # Hindi unit words
    'किमी', 'मी', 'सेमी', 'किग्रा', 'ग्रा', 'ली', 'मिली',
}

# Ordinal suffixes across languages
ORDINAL_SUFFIXES = {
    'st', 'nd', 'rd', 'th',           # English
    'ला', 'रा', 'था', 'वाँ', 'वां', 'वीं',  # Hindi
    'औं', 'वटा',                        # Nepali
    'வது', 'ஆவது', 'ஆம்',               # Tamil
}

# Named entity prefixes
NAMED_ENTITY_PREFIXES = {
    'डॉ.', 'डॉ', 'श्री', 'श्रीमती', 'सुश्री', 'प्रो.', 'प्रो',
    'मो.', 'Dr.', 'Mr.', 'Mrs.', 'Ms.', 'Prof.', 'Sr.', 'Jr.',
    'St.', 'Smt.', 'Shri', 'Km.',
}

# Common context words that hint at categories
CONTEXT_HINTS = {
    'currency': {'रुपये', 'रुपया', 'पैसे', 'कीमत', 'दाम', 'price', 'cost', 'rupees'},
    'date': {'को', 'तारीख', 'दिनांक', 'date', 'जनवरी', 'फ़रवरी', 'मार्च',
             'अप्रैल', 'मई', 'जून', 'जुलाई', 'अगस्त', 'सितंबर',
             'अक्टूबर', 'नवंबर', 'दिसंबर'},
    'time': {'बजे', 'बजकर', 'AM', 'PM', 'am', 'pm', 'सुबह', 'शाम', 'दोपहर', 'रात'},
    'unit': {'प्रति', 'per', 'weight', 'distance', 'वजन', 'दूरी'},
}


class FeatureExtractor:
    """
    Extracts feature vectors from tokens with their surrounding context
    for ML-based category classification.

    Features include:
    - Numeric patterns (has_digits, all_digits, digit_ratio, etc.)
    - Symbol patterns (currency symbols, %, :, /, etc.)
    - Morphological patterns (ordinal suffixes, unit suffixes)
    - Context features (previous and next word indicators)
    - Pattern signatures (D/D/D for dates, D:D for times, etc.)
    """

    def __init__(self):
        self._context_vocab = set()
        self._fitted = False

    def extract_single(self, token, prev_word='', next_word=''):
        """
        Extract features for a single token.

        Args:
            token:     The token string to classify
            prev_word: The word before this token (empty string if none)
            next_word: The word after this token (empty string if none)

        Returns:
            dict of feature_name -> float
        """
        features = {}

        # ── Basic token properties ────────────────────────────────
        features['token_length'] = len(token)
        features['has_digits'] = float(bool(re.search(r'\d', token)))
        features['all_digits'] = float(token.isdigit())
        features['has_alpha'] = float(bool(re.search(r'[a-zA-Z\u0900-\u097F\u0B80-\u0BFF\u0980-\u09FF]', token)))

        # Digit ratio
        digit_count = sum(1 for c in token if c.isdigit())
        features['digit_ratio'] = digit_count / max(len(token), 1)

        # ── Decimal / fraction patterns ───────────────────────────
        features['has_decimal'] = float('.' in token and bool(re.search(r'\d\.\d', token)))
        features['has_comma_number'] = float(bool(re.match(r'^\d{1,3}(,\d{2,3})*$', token)))

        # ── Currency indicators ───────────────────────────────────
        features['has_currency_symbol'] = float(
            any(sym in token for sym in CURRENCY_SYMBOLS)
        )
        features['starts_with_currency'] = float(
            any(token.startswith(sym) for sym in CURRENCY_SYMBOLS)
        )

        # ── Time indicators ───────────────────────────────────────
        features['has_colon'] = float(':' in token)
        features['is_time_pattern'] = float(bool(
            re.match(r'^\d{1,2}:\d{2}(:\d{2})?$', token)
        ))

        # ── Date indicators ───────────────────────────────────────
        features['has_slash'] = float('/' in token)
        features['has_dash'] = float('-' in token and bool(re.search(r'\d-\d', token)))
        features['is_date_pattern'] = float(bool(
            re.match(r'^\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}$', token)
        ))

        # ── Ordinal indicators ────────────────────────────────────
        features['has_ordinal_suffix'] = float(
            any(token.endswith(suf) for suf in ORDINAL_SUFFIXES)
            and bool(re.search(r'\d', token))
        )

        # ── Unit indicators ───────────────────────────────────────
        features['has_unit_suffix'] = float(
            any(token.endswith(suf) for suf in UNIT_SUFFIXES)
            and bool(re.search(r'\d', token))
        )

        # ── Percentage ────────────────────────────────────────────
        features['has_percent'] = float('%' in token)

        # ── Named entity indicators ───────────────────────────────
        features['is_named_entity'] = float(token in NAMED_ENTITY_PREFIXES)
        features['starts_with_upper'] = float(
            len(token) > 0 and token[0].isupper()
        )
        features['has_dot'] = float('.' in token and not features['has_decimal'])

        # ── Phone number indicators ───────────────────────────────
        clean_phone = re.sub(r'[\s\-\(\)\+]', '', token)
        features['is_phone_pattern'] = float(
            clean_phone.isdigit() and 7 <= len(clean_phone) <= 15
        )

        # ── Pattern signature ─────────────────────────────────────
        # Convert token to abstract pattern: D=digit, L=letter, S=symbol
        pattern = self._get_pattern_signature(token)
        features['pattern_has_DSD'] = float('D/D' in pattern or 'D-D' in pattern)
        features['pattern_has_DCD'] = float('D:D' in pattern)
        features['pattern_has_SD'] = float(
            pattern.startswith('S') and 'D' in pattern
        )

        # ── Context features ──────────────────────────────────────
        # Previous word context hints
        for cat, hints in CONTEXT_HINTS.items():
            features[f'prev_hint_{cat}'] = float(prev_word.lower() in hints)
            features[f'next_hint_{cat}'] = float(next_word.lower() in hints)

        # Simple prev/next word features
        features['prev_is_empty'] = float(prev_word == '')
        features['next_is_empty'] = float(next_word == '')
        features['prev_has_digits'] = float(bool(re.search(r'\d', prev_word)))
        features['next_has_digits'] = float(bool(re.search(r'\d', next_word)))

        return features

    def extract_batch(self, tokens):
        """
        Extract features for a list of tokens with context.

        Args:
            tokens: List of token strings (from text.split())

        Returns:
            List of feature dicts, one per token
        """
        results = []
        for i, token in enumerate(tokens):
            prev_word = tokens[i - 1] if i > 0 else ''
            next_word = tokens[i + 1] if i < len(tokens) - 1 else ''
            features = self.extract_single(token, prev_word, next_word)
            results.append(features)
        return results

    def features_to_matrix(self, feature_dicts):
        """
        Convert a list of feature dictionaries to a numpy matrix.

        All dicts must have the same keys (which they will if produced
        by extract_single/extract_batch).

        Returns:
            (np.ndarray, list[str]) — feature matrix and feature names
        """
        if not feature_dicts:
            return np.empty((0, 0)), []

        feature_names = sorted(feature_dicts[0].keys())
        matrix = np.array([
            [fd[name] for name in feature_names]
            for fd in feature_dicts
        ])
        return matrix, feature_names

    @staticmethod
    def _get_pattern_signature(token):
        """
        Convert token to an abstract pattern.
        Digits → D, Letters → L, Everything else → the symbol itself.

        Examples:
            '₹500'      → 'SDDD'
            '15/08/2024' → 'DD/DD/DDDD'
            '10:30'      → 'DD:DD'
            '5kg'        → 'DLL'
        """
        parts = []
        for ch in token:
            if ch.isdigit():
                parts.append('D')
            elif ch.isalpha():
                parts.append('L')
            else:
                parts.append(ch)
        return ''.join(parts)
