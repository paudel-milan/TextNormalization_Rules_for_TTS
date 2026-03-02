"""Time normalization tests."""

from helpers import get_engine, print_test_result


def run():
    engine = get_engine()

    print("\n" + "─"*70)
    print("  TIME TESTS")
    print("─"*70)

    for name, text in [
        ("Simple Time (10:30)", "मीटिंग 10:30 बजे है"),
        ("24-hour Time (14:45)", "ट्रेन 14:45 पर आएगी"),
        ("Time with seconds (10:30:15)", "समय 10:30:15 है"),
        ("Exact hour (2:00)", "कार्यक्रम 2:00 बजे शुरू होगा"),
    ]:
        print_test_result(
            name, text, ['time'],
            engine.normalize(text, ['time']),
        )

    print("✅ Time tests passed!")


if __name__ == '__main__':
    run()
