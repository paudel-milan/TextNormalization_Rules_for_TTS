"""
Shared test utilities for all category tests.
"""

import sys
from pathlib import Path

# Ensure backend/ is on sys.path so 'from engine import ...' works
_backend_dir = str(Path(__file__).resolve().parent.parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from engine import NormalizationEngine

ALL_CATEGORIES = [
    'currency', 'cardinal', 'unit', 'date',
    'time', 'ordinal', 'named_entity',
]


def get_engine(language='hi-IN'):
    """Return a shared engine instance."""
    return NormalizationEngine(language=language)


def print_test_result(test_name, input_text, categories, result):
    """Pretty-print a single test result."""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}")
    print(f"Input: {input_text}")
    print(f"Categories: {', '.join(categories)}")
    print(f"\nNormalized: {result['normalized_text']}")
    print(f"\nDFA Info:")
    for dfa in result['dfa_info']:
        print(f"  - {dfa['category'].upper()}: {dfa['original']}")
        print(f"    States: {' → '.join(dfa['states'])}")
    print(f"\nSSML (first 300 chars):")
    print(f"{result['ssml'][:300]}...")
    print(f"{'='*70}\n")
