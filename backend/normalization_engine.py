"""
Core Normalization Engine
Orchestrates DFA-based detection and rule-based normalization
"""

import json
import re
from pathlib import Path
from dfa_engine import CurrencyDFA, CardinalDFA
from normalizers import CurrencyNormalizer, CardinalNormalizer
from ssml_generator import SSMLGenerator


class NormalizationEngine:
    """
    Main engine that coordinates:
    1. DFA-based token detection
    2. Rule-based normalization
    3. SSML generation
    """
    
    def __init__(self, language='hi-IN'):
        """
        Initialize the normalization engine
        
        Args:
            language: Language code (default: hi-IN for Hindi)
        """
        self.language = language
        
        # Load language resources
        self.resources = self._load_language_resources()
        
        # Initialize DFAs
        self.currency_dfa = CurrencyDFA()
        self.cardinal_dfa = CardinalDFA()
        
        # Initialize normalizers
        self.currency_normalizer = CurrencyNormalizer(self.resources)
        self.cardinal_normalizer = CardinalNormalizer(self.resources)
        
        # Initialize SSML generator
        self.ssml_generator = SSMLGenerator()
        
    def _load_language_resources(self):
        """Load language-specific resources from JSON file"""
        resource_path = Path(__file__).parent / 'resources' / f'{self.language}.json'
        
        with open(resource_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def normalize(self, text, categories):
        """
        Main normalization pipeline
        
        Args:
            text: Input Hindi text
            categories: List of categories to normalize (e.g., ['currency', 'cardinal'])
            
        Returns:
            Dictionary with normalized_text, ssml, and dfa_info
        """
        tokens = []
        dfa_info = []
        
        # Tokenize and detect patterns
        words = text.split()
        i = 0
        
        while i < len(words):
            word = words[i]
            matched = False
            
            # Try currency detection if enabled
            if 'currency' in categories:
                currency_match = self.currency_dfa.match(word)
                if currency_match['matched']:
                    # Look ahead for decimal part if present
                    full_amount = word
                    if i + 1 < len(words) and '.' in word:
                        # Already has decimal
                        pass
                    
                    normalized = self.currency_normalizer.normalize(full_amount)
                    tokens.append({
                        'original': full_amount,
                        'normalized': normalized,
                        'category': 'currency',
                        'dfa_states': currency_match['states']
                    })
                    dfa_info.append({
                        'category': 'currency',
                        'original': full_amount,
                        'states': currency_match['states']
                    })
                    matched = True
            
            # Try cardinal number detection if enabled
            if not matched and 'cardinal' in categories:
                cardinal_match = self.cardinal_dfa.match(word)
                if cardinal_match['matched']:
                    normalized = self.cardinal_normalizer.normalize(word)
                    tokens.append({
                        'original': word,
                        'normalized': normalized,
                        'category': 'cardinal',
                        'dfa_states': cardinal_match['states']
                    })
                    dfa_info.append({
                        'category': 'cardinal',
                        'original': word,
                        'states': cardinal_match['states']
                    })
                    matched = True
            
            # If no match, keep original
            if not matched:
                tokens.append({
                    'original': word,
                    'normalized': word,
                    'category': 'text',
                    'dfa_states': []
                })
            
            i += 1
        
        # Build normalized text
        normalized_text = ' '.join([t['normalized'] for t in tokens])
        
        # Generate SSML
        ssml = self.ssml_generator.generate(tokens)
        
        return {
            'normalized_text': normalized_text,
            'ssml': ssml,
            'dfa_info': dfa_info
        }
