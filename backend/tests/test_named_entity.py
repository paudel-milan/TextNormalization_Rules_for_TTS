"""Named entity normalization tests."""

from helpers import get_engine, print_test_result


def run():
    engine = get_engine()

    print("\n" + "─"*70)
    print("  NAMED ENTITY TESTS")
    print("─"*70)

    for name, text in [
        ("Hindi title (डॉ.)", "डॉ. शर्मा आ रहे हैं"),
        ("Hindi title (श्री)", "श्री मोहन जी से मिलिए"),
        ("English title (Dr.)", "Dr. Kumar ने कहा"),
    ]:
        print_test_result(
            name, text, ['named_entity'],
            engine.normalize(text, ['named_entity']),
        )

    print("✅ Named entity tests passed!")


if __name__ == '__main__':
    run()
