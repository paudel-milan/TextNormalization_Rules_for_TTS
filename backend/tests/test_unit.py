"""Unit normalization tests."""

from helpers import get_engine, print_test_result


def run():
    engine = get_engine()

    print("\n" + "─"*70)
    print("  UNIT TESTS")
    print("─"*70)

    for name, text in [
        ("Weight Unit (5kg)", "मेरा वज़न 5kg है"),
        ("Distance Unit (10km)", "दूरी 10km है"),
        ("Volume Unit (100ml)", "पानी 100ml चाहिए"),
        ("Temperature Unit (25°C)", "तापमान 25°C है"),
        ("Data Unit (500MB)", "डेटा 500MB बचा है"),
    ]:
        print_test_result(
            name, text, ['unit'],
            engine.normalize(text, ['unit']),
        )

    print("✅ Unit tests passed!")


if __name__ == '__main__':
    run()
