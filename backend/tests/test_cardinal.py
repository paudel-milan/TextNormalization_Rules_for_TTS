"""Cardinal number normalization tests."""

from helpers import get_engine, print_test_result


def run():
    engine = get_engine()

    print("\n" + "─"*70)
    print("  CARDINAL TESTS")
    print("─"*70)

    print_test_result(
        "Cardinal Numbers",
        "मुझे 25 किताबें चाहिए",
        ['cardinal'],
        engine.normalize("मुझे 25 किताबें चाहिए", ['cardinal']),
    )

    print_test_result(
        "Large Cardinal (Lakhs/Crores)",
        "जनसंख्या 5000000 है",
        ['cardinal'],
        engine.normalize("जनसंख्या 5000000 है", ['cardinal']),
    )

    print("✅ Cardinal tests passed!")


if __name__ == '__main__':
    run()
