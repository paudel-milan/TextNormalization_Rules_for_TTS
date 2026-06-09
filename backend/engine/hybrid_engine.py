"""
Hybrid Normalization Engine

Orchestrates the 5-step hybrid pipeline:
    Step 1: Tokenize input text
    Step 2: Rule-based detection (DFA/Regex)
    Step 3: ML-based classification (context features)
    Step 4: Combine predictions → select final category
    Step 5: Pass to existing normalizers + SSML generator

The objective is NOT to replace the rule engine. The objective is to
build a hybrid architecture where ML performs category identification
and the existing rule engine performs normalization and SSML generation.
"""

import json
import os
from pathlib import Path

from rule_engine.detector import RuleBasedDetector
from ml_classifier.feature_extractor import FeatureExtractor
from ml_classifier.model import CategoryClassifier
from normalizers import (
    CurrencyNormalizer, CardinalNormalizer,
    UnitNormalizer, DateNormalizer, TimeNormalizer,
    OrdinalNormalizer, NamedEntityNormalizer,
)
from ssml import SSMLGenerator


# Root of the backend package
_BACKEND_DIR = Path(__file__).resolve().parent.parent


class HybridEngine:
    """
    Hybrid detection engine combining Rule-based DFAs with ML classification.

    Per-token output includes:
        - rule_category + rule_confidence
        - ml_category + ml_confidence
        - final_category + final_confidence
        - normalized text
    """

    def __init__(self, language='hi-IN', model_type='logistic_regression'):
        self.language = language
        self.resources = self._load_resources()

        # ── Rule-based detector (reuses existing DFAs) ────────────
        self.rule_detector = RuleBasedDetector(language=language)

        # ── ML classifier ─────────────────────────────────────────
        self.feature_extractor = FeatureExtractor(language=language)
        self.ml_classifier = None
        self.ml_available = False
        self._load_ml_model(model_type)

        # ── Normalizers (reuse existing) ──────────────────────────
        self.normalizers = {
            'currency': CurrencyNormalizer(self.resources),
            'cardinal': CardinalNormalizer(self.resources),
            'unit': UnitNormalizer(self.resources),
            'date': DateNormalizer(self.resources),
            'time': TimeNormalizer(self.resources),
            'ordinal': OrdinalNormalizer(self.resources),
            'named_entity': NamedEntityNormalizer(self.resources),
        }

        # ── DFA instances for normalization (need match data) ─────
        self._init_dfas()

        # ── SSML generator ────────────────────────────────────────
        self.ssml_generator = SSMLGenerator(language=language)

    def _load_resources(self):
        """Load language-specific resources."""
        path = _BACKEND_DIR / 'resources' / f'{self.language}.json'
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_ml_model(self, model_type):
        """Try to load a pre-trained ML model."""
        try:
            self.ml_classifier = CategoryClassifier(model_type=model_type)
            self.ml_classifier.load(language=self.language)
            self.ml_available = True
        except (FileNotFoundError, ImportError):
            self.ml_available = False
            self.ml_classifier = None

    def _init_dfas(self):
        """Initialize DFA instances for extracting match data during normalization."""
        from dfa import (
            CurrencyDFA, CardinalDFA, UnitDFA,
            DateDFA, TimeDFA, OrdinalDFA, NamedEntityDFA,
        )

        patterns = self.resources.get('patterns', {})

        self.dfas = {
            'currency': CurrencyDFA(patterns={
                'currency_symbol': patterns.get('currency_symbol'),
                'currency_strip': patterns.get('currency_strip'),
            }),
            'cardinal': CardinalDFA(pattern=patterns.get('cardinal')),
            'unit': UnitDFA(pattern=patterns.get('unit')),
            'date': DateDFA(pattern=patterns.get('date')),
            'time': TimeDFA(pattern=patterns.get('time')),
            'ordinal': OrdinalDFA(pattern=patterns.get('ordinal')),
        }

        ne_keys = list(
            self.resources.get('named_entities', {}).get('abbreviations', {}).keys()
        )
        self.dfas['named_entity'] = NamedEntityDFA(known_entities=ne_keys)

    # ──────────────────────────────────────────────────────────────
    #  Main hybrid pipeline
    # ──────────────────────────────────────────────────────────────

    def normalize(self, text):
        """
        Run the full 5-step hybrid normalization pipeline.

        Args:
            text: Input text string

        Returns:
            dict with:
                normalized_text: Full normalized string
                ssml:            SSML output
                token_details:   Per-token breakdown (rule/ML/final categories)
                pipeline_summary: Stats about the detection
        """
        # ── Step 1: Tokenize ──────────────────────────────────────
        words = text.split()
        if not words:
            return {
                'normalized_text': '',
                'ssml': '',
                'token_details': [],
                'pipeline_summary': {'total_tokens': 0, 'detected_tokens': 0, 'categories_found': []},
            }

        # ── Step 2: Rule-based detection ──────────────────────────
        rule_results = []
        for word in words:
            rule_result = self.rule_detector.detect(word)
            rule_results.append(rule_result)

        # ── Step 3: ML-based classification ───────────────────────
        ml_results = []
        if self.ml_available and self.ml_classifier:
            feature_dicts = self.feature_extractor.extract_batch(words)
            ml_predictions = self.ml_classifier.predict(feature_dicts)
            ml_results = ml_predictions
        else:
            # No ML model available — fill with empty predictions
            ml_results = [
                {'category': 'text', 'confidence': 0.0, 'all_scores': {}}
                for _ in words
            ]

        # ── Step 4: Combine predictions ───────────────────────────
        token_details = []
        for i, word in enumerate(words):
            rule = rule_results[i]
            ml = ml_results[i]

            final_category, final_confidence = self._combine_predictions(
                rule_category=rule['category'],
                rule_confidence=rule['confidence'],
                ml_category=ml['category'],
                ml_confidence=ml['confidence'],
            )

            token_details.append({
                'token': word,
                'rule_category': rule['category'],
                'rule_confidence': round(rule['confidence'], 4),
                'ml_category': ml['category'],
                'ml_confidence': round(ml['confidence'], 4),
                'final_category': final_category,
                'final_confidence': round(final_confidence, 4),
                'dfa_states': rule.get('dfa_states', []),
            })

        # ── Step 5: Normalize using existing normalizers ──────────
        normalized_tokens = []
        for detail in token_details:
            word = detail['token']
            category = detail['final_category']

            normalized = self._normalize_token(word, category, words)
            detail['normalized'] = normalized

            normalized_tokens.append({
                'original': word,
                'normalized': normalized,
                'category': category,
                'dfa_states': detail['dfa_states'],
            })

        # Build final output
        normalized_text = ' '.join(d['normalized'] for d in token_details)
        ssml = self.ssml_generator.generate(normalized_tokens)

        categories_found = sorted(set(
            d['final_category'] for d in token_details
            if d['final_category'] != 'text'
        ))

        return {
            'normalized_text': normalized_text,
            'ssml': ssml,
            'token_details': token_details,
            'pipeline_summary': {
                'total_tokens': len(words),
                'detected_tokens': sum(
                    1 for d in token_details if d['final_category'] != 'text'
                ),
                'categories_found': categories_found,
                'ml_model_used': self.ml_available,
            },
        }

    def _combine_predictions(self, rule_category, rule_confidence,
                              ml_category, ml_confidence):
        """
        Combine rule-based and ML predictions to select final category.

        Logic:
            1. If both agree → use that category (max confidence)
            2. If only rule matches (non-text) → use rule (confidence 0.9)
            3. If only ML matches (non-text) → use ML if confidence > 0.6
            4. If they disagree → prefer rule if rule_confidence >= 0.7, else ML
            5. Fallback: 'text'
        """
        rule_is_text = (rule_category == 'text')
        ml_is_text = (ml_category == 'text')

        # Case 1: Both agree
        if rule_category == ml_category:
            return rule_category, max(rule_confidence, ml_confidence)

        # Case 2: Only rule matches
        if not rule_is_text and ml_is_text:
            return rule_category, rule_confidence

        # Case 3: Only ML matches
        if rule_is_text and not ml_is_text:
            if ml_confidence > 0.6:
                return ml_category, ml_confidence
            else:
                return 'text', 0.0

        # Case 4: Both match but disagree
        if not rule_is_text and not ml_is_text:
            # if rule_confidence >= 0.7:
            #     return rule_category, rule_confidence
            # elif ml_confidence > rule_confidence:
            #     return ml_category, ml_confidence
            # else:
            #     return rule_category, rule_confidence
            if ml_confidence>=0.5:
                return ml_category,ml_confidence
            else:
                return rule_category,rule_confidence

        # Case 5: Both are text
        return 'text', 0.0

    def _normalize_token(self, word, category, all_words):
        """
        Normalize a single token using the appropriate normalizer.

        Uses the existing normalizer classes — same logic as NormalizationEngine
        but applied per-token based on the hybrid-detected category.
        """
        if category == 'text':
            return word

        try:
            if category == 'currency':
                return self.normalizers['currency'].normalize(word)

            elif category == 'cardinal':
                return self.normalizers['cardinal'].normalize(word)

            elif category == 'date':
                dfa = self.dfas.get('date')
                if dfa:
                    result = dfa.match(word)
                    if result.get('matched'):
                        return self.normalizers['date'].normalize(
                            word,
                            day=result.get('day'),
                            month=result.get('month'),
                            year=result.get('year'),
                        )
                return word

            elif category == 'time':
                dfa = self.dfas.get('time')
                if dfa:
                    result = dfa.match(word)
                    if result.get('matched'):
                        return self.normalizers['time'].normalize(
                            word,
                            hour=result.get('hour'),
                            minute=result.get('minute'),
                            second=result.get('second'),
                            period=result.get('period'),
                        )
                return word

            elif category == 'unit':
                dfa = self.dfas.get('unit')
                if dfa:
                    result = dfa.match(word)
                    if result.get('matched'):
                        return self.normalizers['unit'].normalize(
                            word,
                            number_str=result.get('number'),
                            unit_str=result.get('unit'),
                        )
                return word

            elif category == 'ordinal':
                dfa = self.dfas.get('ordinal')
                if dfa:
                    result = dfa.match(word)
                    if result.get('matched'):
                        return self.normalizers['ordinal'].normalize(
                            word,
                            number_str=result.get('number'),
                        )
                return word

            elif category == 'named_entity':
                return self.normalizers['named_entity'].normalize(word)

            elif category == 'phone_number':
                # Phone number: read digit by digit
                return self.normalizers['cardinal'].normalize(word)

            else:
                return word

        except Exception:
            # If normalization fails, return original token
            return word

    def get_model_status(self):
        """Return status of the ML model for this language."""
        available_models = CategoryClassifier.get_available_models(self.language)
        return {
            'language': self.language,
            'ml_available': self.ml_available,
            'available_models': available_models,
            'current_model': self.ml_classifier.model_type if self.ml_classifier else None,
        }
