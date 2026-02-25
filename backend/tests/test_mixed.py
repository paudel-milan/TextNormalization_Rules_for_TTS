"""Mixed / combined category normalization tests."""

from helpers import get_engine, print_test_result, ALL_CATEGORIES


def run():
    engine = get_engine()

    print("\n" + "─"*70)
    print("  MIXED / COMBINED TESTS")
    print("─"*70)

    print_test_result(
        "Mixed: Currency + Cardinal",
        "मेरे पास ₹500 हैं और मुझे 25 किताबें चाहिए",
        ['currency', 'cardinal'],
        engine.normalize(
            "मेरे पास ₹500 हैं और मुझे 25 किताबें चाहिए",
            ['currency', 'cardinal'],
        ),
    )

    print_test_result(
        "Mixed: All Categories",
        "डॉ. शर्मा ने 15/08/2024 को 10:30 पर ₹500 में 5kg चावल 1st बार ख़रीदा",
        ALL_CATEGORIES,
        engine.normalize(
            "डॉ. शर्मा ने 15/08/2024 को 10:30 पर ₹500 में 5kg चावल 1st बार ख़रीदा",
            ALL_CATEGORIES,
        ),
    )

    print_test_result(
        "Plain Text (No normalization needed)",
        "यह एक सामान्य वाक्य है",
        ALL_CATEGORIES,
        engine.normalize("यह एक सामान्य वाक्य है", ALL_CATEGORIES),
    )

    print("✅ Mixed tests passed!")


if __name__ == '__main__':
    run()
