"""Date normalization tests."""

from helpers import get_engine, print_test_result


def run():
    engine = get_engine()

    print("\n" + "─"*70)
    print("  DATE TESTS")
    print("─"*70)

    for name, text in [
        ("Date with slash (15/08/2024)", "स्वतंत्रता दिवस 15/08/2024 को है"),
        ("Date with dash (01-01-2025)", "नया साल 01-01-2025 से शुरू होगा"),
        ("Date with dot (26.01.2026)", "गणतंत्र दिवस 26.01.2026 को है"),
    ]:
        print_test_result(
            name, text, ['date'],
            engine.normalize(text, ['date']),
        )

    print("✅ Date tests passed!")


if __name__ == '__main__':
    run()
