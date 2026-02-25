"""Ordinal normalization tests."""

from helpers import get_engine, print_test_result


def run():
    engine = get_engine()

    print("\n" + "─"*70)
    print("  ORDINAL TESTS")
    print("─"*70)

    for name, text in [
        ("Ordinal 1st", "वह 1st स्थान पर है"),
        ("Ordinal 5th", "वह 5th कक्षा में है"),
        ("Ordinal 21st", "आज 21st सदी है"),
        ("Hindi ordinal suffix (3रा)", "उसका 3रा प्रयास सफल रहा"),
    ]:
        print_test_result(
            name, text, ['ordinal'],
            engine.normalize(text, ['ordinal']),
        )

    print("✅ Ordinal tests passed!")


if __name__ == '__main__':
    run()
