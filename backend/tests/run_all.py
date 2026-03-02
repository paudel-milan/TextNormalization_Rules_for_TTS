"""
Run all normalization tests across all categories.
Usage: python tests/run_all.py
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

import test_currency
import test_cardinal
import test_unit
import test_date
import test_time
import test_ordinal
import test_named_entity
import test_mixed


def main():
    print("\n" + "="*70)
    print("Text Normalization — Full Test Suite (7 Categories)")
    print("="*70)

    test_currency.run()
    test_cardinal.run()
    test_unit.run()
    test_date.run()
    test_time.run()
    test_ordinal.run()
    test_named_entity.run()
    test_mixed.run()

    print("\n✅ All tests completed successfully!\n")


if __name__ == '__main__':
    main()
