"""
Test Cases for Hindi Text Normalization Framework
Run with: python test_normalization.py
"""

from normalization_engine import NormalizationEngine


def print_test_result(test_name, input_text, categories, result):
    """Pretty print test results"""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}")
    print(f"Input: {input_text}")
    print(f"Categories: {', '.join(categories)}")
    print(f"\nNormalized: {result['normalized_text']}")
    print(f"\nDFA Info:")
    for dfa in result['dfa_info']:
        print(f"  - {dfa['category'].upper()}: {dfa['original']}")
        print(f"    States: {' → '.join(dfa['states'])}")
    print(f"\nSSML (first 200 chars):")
    print(f"{result['ssml'][:200]}...")
    print(f"{'='*70}\n")


def run_tests():
    """Run comprehensive test suite"""
    
    # Initialize engine
    engine = NormalizationEngine(language='hi-IN')
    
    # Test 1: Simple currency
    print_test_result(
        "Simple Currency (₹500)",
        "मेरे पास ₹500 हैं",
        ['currency'],
        engine.normalize("मेरे पास ₹500 हैं", ['currency'])
    )
    
    # Test 2: Currency with decimal
    print_test_result(
        "Currency with Decimal (₹500.50)",
        "कीमत ₹500.50 है",
        ['currency'],
        engine.normalize("कीमत ₹500.50 है", ['currency'])
    )
    
    # Test 3: Large currency amount
    print_test_result(
        "Large Currency (₹125000)",
        "वेतन ₹125000 प्रति माह है",
        ['currency'],
        engine.normalize("वेतन ₹125000 प्रति माह है", ['currency'])
    )
    
    # Test 4: Cardinal numbers
    print_test_result(
        "Cardinal Numbers",
        "मुझे 25 किताबें चाहिए",
        ['cardinal'],
        engine.normalize("मुझे 25 किताबें चाहिए", ['cardinal'])
    )
    
    # Test 5: Mixed (currency + cardinal)
    print_test_result(
        "Mixed Categories",
        "मेरे पास ₹500 हैं और मुझे 25 किताबें चाहिए",
        ['currency', 'cardinal'],
        engine.normalize("मेरे पास ₹500 हैं और मुझे 25 किताबें चाहिए", ['currency', 'cardinal'])
    )
    
    # Test 6: Complex sentence
    print_test_result(
        "Complex Sentence",
        "कुल 100 छात्रों ने ₹1250.50 का शुल्क जमा किया",
        ['currency', 'cardinal'],
        engine.normalize("कुल 100 छात्रों ने ₹1250.50 का शुल्क जमा किया", ['currency', 'cardinal'])
    )
    
    # Test 7: Large numbers
    print_test_result(
        "Large Numbers (Lakhs and Crores)",
        "जनसंख्या 5000000 है और बजट ₹10000000 है",
        ['currency', 'cardinal'],
        engine.normalize("जनसंख्या 5000000 है और बजट ₹10000000 है", ['currency', 'cardinal'])
    )
    
    # Test 8: Only text (no normalization needed)
    print_test_result(
        "Plain Text (No Numbers)",
        "यह एक सामान्य वाक्य है",
        ['currency', 'cardinal'],
        engine.normalize("यह एक सामान्य वाक्य है", ['currency', 'cardinal'])
    )
    
    print("\n✅ All tests completed successfully!\n")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("Hindi Text Normalization - Test Suite")
    print("="*70)
    run_tests()
