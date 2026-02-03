# Hindi Text Normalization Framework for TTS

A production-grade, rule-based Text Normalization (TN) framework for Hindi Text-to-Speech systems. This project implements DFA-based pattern detection and deterministic normalization rules, designed for enterprise TTS applications like Samsung Bixby and Galaxy AI.

## 🎯 Project Overview

This framework converts raw Hindi text into normalized spoken form suitable for TTS synthesis. It uses **Deterministic Finite Automata (DFA)** for pattern recognition and **rule-based transformations** for text normalization.

### Key Features

- ✅ **Rule-Based Approach**: Deterministic, explainable normalization (no ML/neural models)
- ✅ **DFA-Driven Detection**: State machine-based pattern recognition
- ✅ **SSML Generation**: Automatic Speech Synthesis Markup Language output
- ✅ **Indian Number System**: Full support for lakhs and crores
- ✅ **Modular Architecture**: Clean separation of concerns for easy extension
- ✅ **Language Abstraction**: Hindi-specific data externalized to JSON resources

### Supported Categories

| Category | Example Input | Normalized Output |
|----------|--------------|-------------------|
| **Currency** | ₹500 | पाँच सौ रुपये |
| **Currency (Decimal)** | ₹500.50 | पाँच सौ रुपये पचास पैसे |
| **Cardinal Numbers** | 123 | एक सौ तेईस |
| **Large Numbers** | 125000 | एक लाख पच्चीस हज़ार |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (HTML/CSS/JS)                   │
│              Category Selection & Text Input                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP REST API
┌──────────────────────▼──────────────────────────────────────┐
│                   Backend (Flask API)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Normalization Engine (Core)                     │
│  ┌────────────────────────────────────────────────────┐    │
│  │  1. DFA-Based Token Detection                      │    │
│  │     • CurrencyDFA: ₹500 pattern matching           │    │
│  │     • CardinalDFA: Number pattern matching         │    │
│  └────────────────────┬───────────────────────────────┘    │
│  ┌────────────────────▼───────────────────────────────┐    │
│  │  2. Rule-Based Normalization                       │    │
│  │     • NumberToWordsConverter (Indian system)       │    │
│  │     • CurrencyNormalizer                           │    │
│  │     • CardinalNormalizer                           │    │
│  └────────────────────┬───────────────────────────────┘    │
│  ┌────────────────────▼───────────────────────────────┐    │
│  │  3. SSML Generation                                │    │
│  │     • Category-specific markup                     │    │
│  │     • Prosody hints for TTS                        │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│           Language Resources (hi-IN.json)                    │
│  • Number words (0-99 + scales)                             │
│  • Currency units (रुपया/रुपये, पैसा/पैसे)                 │
│  • Grammar rules                                            │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
samsumg_TN_TTS/
├── backend/
│   ├── app.py                    # Flask API server
│   ├── normalization_engine.py   # Main orchestration engine
│   ├── dfa_engine.py             # DFA implementations
│   ├── normalizers.py            # Rule-based normalizers
│   ├── ssml_generator.py         # SSML output generator
│   ├── test_normalization.py     # Test suite
│   ├── requirements.txt          # Python dependencies
│   └── resources/
│       └── hi-IN.json            # Hindi language resources
├── frontend/
│   ├── index.html                # UI structure
│   ├── styles.css                # Modern styling
│   └── script.js                 # Frontend logic
└── README.md                     # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Modern web browser
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd samsumg_TN_TTS
   ```

2. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Start the backend server**
   ```bash
   python app.py
   ```
   Server will start at `http://localhost:5000`

4. **Open the frontend**
   - Open `frontend/index.html` in your web browser
   - Or use a local server:
     ```bash
     cd frontend
     python -m http.server 8000
     ```
   - Navigate to `http://localhost:8000`

### Running Tests

```bash
cd backend
python test_normalization.py
```

## 🔍 How It Works

### 1. DFA-Based Pattern Detection

Each normalization category has a dedicated DFA (Deterministic Finite Automaton):

#### Currency DFA Example
```
Input: "₹500.50"

State Transitions:
START → CURRENCY_SYMBOL (₹) → INTEGER_PART (500) 
      → DECIMAL_POINT (.) → DECIMAL_PART (50) → END

States Traversed: ['START', 'CURRENCY_SYMBOL', 'INTEGER_PART', 
                   'DECIMAL_POINT', 'DECIMAL_PART', 'END']
```

#### Cardinal DFA Example
```
Input: "123"

State Transitions:
START → DIGIT (1) → DIGIT (2) → DIGIT (3) → END
```

### 2. Rule-Based Normalization

The `NumberToWordsConverter` uses the **Indian numbering system**:

| Scale | Value | Hindi |
|-------|-------|-------|
| Ones | 1-9 | एक, दो, तीन... |
| Tens | 10-99 | दस, बीस, तीस... |
| Hundred | 100 | सौ |
| Thousand | 1,000 | हज़ार |
| Lakh | 1,00,000 | लाख |
| Crore | 1,00,00,000 | करोड़ |

**Example Conversion:**
```
125000 → "एक लाख पच्चीस हज़ार"
(1 lakh + 25 thousand)
```

### 3. SSML Generation

Generated SSML includes proper markup for TTS engines:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="hi-IN">
  <say-as interpret-as="currency" format="long">
    <emphasis level="moderate">पाँच सौ रुपये</emphasis>
  </say-as>
</speak>
```

## 📝 Usage Examples

### Example 1: Currency Normalization
```
Input:  "मेरे पास ₹500 हैं"
Output: "मेरे पास पाँच सौ रुपये हैं"
```

### Example 2: Currency with Decimal
```
Input:  "कीमत ₹1250.50 है"
Output: "कीमत एक हज़ार दो सौ पचास रुपये पचास पैसे है"
```

### Example 3: Cardinal Numbers
```
Input:  "मुझे 25 किताबें चाहिए"
Output: "मुझे पच्चीस किताबें चाहिए"
```

### Example 4: Mixed Categories
```
Input:  "100 छात्रों ने ₹500 जमा किया"
Output: "एक सौ छात्रों ने पाँच सौ रुपये जमा किया"
```

## 🔧 Extending to Other Languages

The framework is designed for easy language extension:

1. **Create new language resource file**: `resources/ta-IN.json` (for Tamil)
2. **Define language-specific mappings**:
   - Number words
   - Currency units
   - Grammar rules
3. **Update DFA patterns** (if needed for language-specific symbols)
4. **No code changes required** in core engine!

### Example: Adding Tamil Support

```json
{
  "language": "ta-IN",
  "numbers": {
    "ones": {
      "1": "ஒன்று",
      "2": "இரண்டு",
      ...
    }
  },
  "currency": {
    "main_unit": {
      "singular": "ரூபாய்",
      "plural": "ரூபாய்கள்"
    }
  }
}
```

## 🧪 Test Cases

The project includes 8 comprehensive test cases:

1. ✅ Simple currency (₹500)
2. ✅ Currency with decimal (₹500.50)
3. ✅ Large currency (₹125000)
4. ✅ Cardinal numbers (25)
5. ✅ Mixed categories
6. ✅ Complex sentences
7. ✅ Lakhs and crores (5000000)
8. ✅ Plain text (no normalization)

## 🎓 Educational Value

This project demonstrates:

- **DFA Theory**: Practical application of finite automata
- **Rule-Based NLP**: Deterministic text processing
- **Indian Numbering**: Proper handling of lakhs/crores
- **SSML Standards**: Speech synthesis markup
- **Modular Design**: Clean architecture patterns
- **Language Abstraction**: Resource-driven localization

## 🚧 Future Enhancements

- [ ] Date normalization (e.g., "15/08/2024" → "पंद्रह अगस्त दो हज़ार चौबीस")
- [ ] Time normalization (e.g., "10:30" → "दस बजकर तीस मिनट")
- [ ] Ordinal numbers (e.g., "1st" → "पहला")
- [ ] Phone numbers
- [ ] Abbreviations expansion
- [ ] Support for other Indian languages (Tamil, Telugu, Kannada)

## 📄 License

This project is created for educational and internship purposes.

## 👨‍💻 Author

Created as a production-grade internship project demonstrating rule-based text normalization for enterprise TTS systems.

---

**Note**: This is a deterministic, rule-based system. For production deployment, consider adding:
- Comprehensive error handling
- Logging and monitoring
- Performance optimization
- Edge case handling
- Unit test coverage
- API rate limiting
- Security measures
