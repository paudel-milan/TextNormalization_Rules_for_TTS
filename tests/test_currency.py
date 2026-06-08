"""Currency normalization tests."""

from helpers import get_engine, print_test_result


def run():
    engine = get_engine()

    print("\n" + "─"*70)
    print("  CURRENCY TESTS")
    print("─"*70)

    print_test_result(
        "Simple Currency (₹500)",
        "मेरे पास ₹500 हैं",
        ['currency'],
        engine.normalize("मेरे पास ₹500 हैं", ['currency']),
    )

    print_test_result(
        "Currency with Decimal (₹500.50)",
        "कीमत ₹500.50 है",
        ['currency'],
        engine.normalize("कीमत ₹500.50 है", ['currency']),
    )

    print_test_result(
        "Large Currency (₹125000)",
        "वेतन ₹125000 प्रति माह है",
        ['currency'],
        engine.normalize("वेतन ₹125000 प्रति माह है", ['currency']),
    )

    print("✅ Currency tests passed!")


if __name__ == '__main__':
    run()
