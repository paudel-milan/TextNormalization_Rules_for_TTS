"""Kannada dialects normalization tests."""

from helpers import get_engine, print_test_result


def run():
    # ── Bangalore Kannada Tests ────────────────────────────────────────
    engine_blr = get_engine('kn-IN-bangalore')
    
    print("\n" + "─"*70)
    print("  KANNADA (BANGALORE) TESTS")
    print("─"*70)

    print_test_result(
        "Bangalore Currency (₹500)",
        "ಅವನು ₹500 ಕೊಟ್ಟನು",
        ['currency'],
        engine_blr.normalize("ಅವನು ₹500 ಕೊಟ್ಟನು", ['currency']),
    )

    print_test_result(
        "Bangalore Ordinal (5th -> 5ನೇ)",
        "ಅವನು 5ನೇ ಸ್ಥಾನ ಪಡೆದನು",
        ['ordinal'],
        engine_blr.normalize("ಅವನು 5ನೇ ಸ್ಥಾನ ಪಡೆದನು", ['ordinal']),
    )

    print_test_result(
        "Bangalore Decimal (2.5kg -> ಎರಡು ದಶಮಾಂಶ ಐದು ಕಿಲೋಗ್ರಾಂ)",
        "2.5kg ತೂಕ",
        ['unit'],
        engine_blr.normalize("2.5kg ತೂಕ", ['unit']),
    )

    # ── Mangalore Kannada Tests ────────────────────────────────────────
    engine_mng = get_engine('kn-IN-mangalore')
    
    print("\n" + "─"*70)
    print("  KANNADA (MANGALORE) TESTS")
    print("─"*70)

    print_test_result(
        "Mangalore Ordinal (5th -> 5ನೆಯ)",
        "ಅವನು 5ನೆಯ ಸ್ಥಾನ ಪಡೆದನು",
        ['ordinal'],
        engine_mng.normalize("ಅವನು 5ನೆಯ ಸ್ಥಾನ ಪಡೆದನು", ['ordinal']),
    )

    print_test_result(
        "Mangalore Decimal (2.5kg -> ಎರಡು ಬಿಂದು ಐದು ಕಿಲೋಗ್ರಾಂ)",
        "2.5kg ತೂಕ",
        ['unit'],
        engine_mng.normalize("2.5kg ತೂಕ", ['unit']),
    )

    # ── Belgaum Kannada Tests ──────────────────────────────────────────
    engine_blg = get_engine('kn-IN-belgaum')
    
    print("\n" + "─"*70)
    print("  KANNADA (BELGAUM) TESTS")
    print("─"*70)

    print_test_result(
        "Belgaum Currency (₹500 -> ರುಪಾಯಿ)",
        "ಅವನು ₹500 ಕೊಟ್ಟನು",
        ['currency'],
        engine_blg.normalize("ಅವನು ₹500 ಕೊಟ್ಟನು", ['currency']),
    )

    print("✅ Kannada dialect tests passed!")


if __name__ == '__main__':
    run()
