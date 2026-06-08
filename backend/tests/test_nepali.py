"""
Comprehensive tests for Nepali (ne-NP) normalization.
"""

import sys
from pathlib import Path

# Ensure backend/ and tests/ are on sys.path
_backend_dir = str(Path(__file__).resolve().parent.parent)
_tests_dir = str(Path(__file__).resolve().parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
if _tests_dir not in sys.path:
    sys.path.insert(0, _tests_dir)

from helpers import get_engine, print_test_result

def run():
    engine = get_engine(language='ne-NP')

    print("\n" + "═"*70)
    print("  NEPALI (ne-NP) NORMALIZATION TESTS")
    print("═"*70)

    test_cases = [
        ("Currency (रु500.50)", "यो रु500.50 हो", ['currency']),
        ("Time (10:30 AM)", "कार्यक्रम 10:30 AM मा छ", ['time']),
        ("Time (14:45)", "बस 14:45 मा आउँछ", ['time']),
        ("Date (15/08/2024)", "आज १५/०८/२०२४ हो", ['date']), # testing with devnagari digits if DFA supports it (it doesn't yet, so 15/08/2024)
        ("Date (15/08/2024) ASCII", "मिति 15/08/2024 हो", ['date']),
        ("Cardinal (1234)", "जम्मा 1234 जना छन्", ['cardinal']),
        ("Ordinal (1st, 5औं)", "उनी 1st र उनी 5औं भए", ['ordinal']),
        ("Unit (10km, 25°C)", "दुरी 10km छ र तापक्रम 25°C छ", ['unit']),
        ("Named Entity (डा.)", "डा. राम श्रेष्ठ", ['named_entity']),
    ]

    for name, text, categories in test_cases:
        print_test_result(
            name, text, categories,
            engine.normalize(text, categories),
        )

    print("✅ Nepali tests completed!")

if __name__ == '__main__':
    run()
