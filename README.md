# Hindi Text Normalization Framework for TTS

A production-grade, rule-based Text Normalization (TN) framework for Hindi Text-to-Speech systems. This project implements DFA-based pattern detection and deterministic normalization rules, designed for enterprise TTS applications like Samsung Bixby and Galaxy AI.

## 🎯 Project Overview

This framework converts raw Hindi text into normalized spoken form suitable for TTS synthesis. It uses **Deterministic Finite Automata (DFA)** for pattern recognition and **rule-based transformations** for text normalization.

### Key Features

- ✅ **Rule-Based Approach**: Deterministic, explainable normalization (no ML/neural models)
- ✅ **DFA-Driven Detection**: State machine-based pattern recognition for 7 categories
- ✅ **SSML Generation**: Automatic Speech Synthesis Markup Language output
- ✅ **Indian Number System**: Full support for lakhs and crores
- ✅ **Modular Architecture**: Clean separation of concerns for easy extension
- ✅ **Language Abstraction**: All language-specific data externalized to JSON — add a new language by adding one file

### Supported Categories (7)

| Category | Example Input | Normalized Output (Hindi) |
|----------|--------------|---------------------------|
| **Currency** | `₹500` | पाँच सौ रुपये |
| **Currency (Decimal)** | `₹500.50` | पाँच सौ रुपये पचास पैसे |
| **Cardinal Numbers** | `123` | एक सौ तेईस |
| **Large Numbers** | `125000` | एक लाख पच्चीस हज़ार |
| **Units** | `5kg` | पाँच किलोग्राम |
| **Date** | `15/08/2024` | पंद्रह अगस्त दो हज़ार चौबीस |
| **Time** | `10:30` | दस बजकर तीस मिनट |
| **Ordinal** | `5th` | पाँचवाँ |
| **Named Entity** | `डॉ.` | डॉक्टर |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (HTML/CSS/JS)                   │
│         Category Checkboxes (7) & Text Input                │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP REST API (POST /api/normalize)
┌──────────────────────▼──────────────────────────────────────┐
│                   Backend (Flask API)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Normalization Engine (Core Pipeline)            │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │  1. DFA-Based Token Detection (Priority Order)     │    │
│  │     • DateDFA        • TimeDFA                     │    │
│  │     • CurrencyDFA    • UnitDFA                     │    │
│  │     • OrdinalDFA     • NamedEntityDFA              │    │
│  │     • CardinalDFA                                  │    │
│  └────────────────────┬───────────────────────────────┘    │
│  ┌────────────────────▼───────────────────────────────┐    │
│  │  2. Rule-Based Normalization                       │    │
│  │     • NumberToWordsConverter (Indian system)       │    │
│  │     • CurrencyNormalizer  • UnitNormalizer         │    │
│  │     • DateNormalizer      • TimeNormalizer         │    │
│  │     • OrdinalNormalizer   • NamedEntityNormalizer  │    │
│  │     • CardinalNormalizer                           │    │
│  └────────────────────┬───────────────────────────────┘    │
│  ┌────────────────────▼───────────────────────────────┐    │
│  │  3. SSML Generation                                │    │
│  │     • <say-as> tags per category                   │    │
│  │     • <sub alias="..."> for named entities         │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│           Language Resources (resources/<lang>.json)         │
│  • Number words (0-99 + scales)                             │
│  • Currency units • Unit mappings   • Month names           │
│  • Time words     • Ordinal forms   • Named entity lookup   │
│  • Grammar rules                                            │
└─────────────────────────────────────────────────────────────┘
```

### Detection Priority

The engine processes tokens in this order to avoid ambiguity:

```
date → time → currency → unit → ordinal → named_entity → cardinal
```

> **Why?** A token like `15/08/2024` must be matched as a **date**, not as three separate cardinal numbers. Similarly, `10:30` must be matched as **time** before cardinal.

---

## 📁 Project Structure

```
samsumg_TN_TTS/
├── backend/
│   ├── app.py                        # Flask API server
│   ├── __init__.py
│   ├── requirements.txt
│   ├── engine/
│   │   ├── __init__.py
│   │   └── normalization_engine.py   # Core orchestrator
│   ├── dfa/
│   │   ├── __init__.py               # Re-exports all DFAs
│   │   ├── base.py                   # BaseDFA abstract class
│   │   ├── currency.py               # CurrencyDFA
│   │   ├── cardinal.py               # CardinalDFA
│   │   ├── unit.py                   # UnitDFA
│   │   ├── date.py                   # DateDFA
│   │   ├── time.py                   # TimeDFA
│   │   ├── ordinal.py                # OrdinalDFA
│   │   └── named_entity.py           # NamedEntityDFA
│   ├── normalizers/
│   │   ├── __init__.py               # Re-exports all normalizers
│   │   ├── number_converter.py       # NumberToWordsConverter
│   │   ├── currency.py               # CurrencyNormalizer
│   │   ├── cardinal.py               # CardinalNormalizer
│   │   ├── unit.py                   # UnitNormalizer
│   │   ├── date.py                   # DateNormalizer
│   │   ├── time.py                   # TimeNormalizer
│   │   ├── ordinal.py                # OrdinalNormalizer
│   │   └── named_entity.py           # NamedEntityNormalizer
│   ├── ssml/
│   │   ├── __init__.py
│   │   └── generator.py              # SSMLGenerator
│   ├── resources/
│   │   ├── hi-IN.json                # Hindi language resources
│   │   └── ne-NP.json                # Nepali language resources
│   └── tests/
│       ├── __init__.py
│       ├── helpers.py                # Shared test utilities
│       ├── test_currency.py
│       ├── test_cardinal.py
│       ├── test_unit.py
│       ├── test_date.py
│       ├── test_time.py
│       ├── test_ordinal.py
│       ├── test_named_entity.py
│       ├── test_mixed.py
│       └── run_all.py                # Run entire test suite
├── frontend/
│   ├── index.html                    # UI with language selector + 7 categories
│   ├── styles.css                    # Modern dark-theme styling
│   └── script.js                     # Frontend logic
├── README.md
└── QUICKSTART.md
```


---

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
python tests/run_all.py
```

Or run a single category:

```bash
python tests/test_currency.py
```

All **22 test cases** will run across all 7 categories.

---

## 🔍 How It Works — Category by Category

### 1. Currency

**DFA**: Detects `₹`, `रु`, `Rs`, `Rs.`, `INR` followed by digits and optional decimals.

```
Input: "₹500.50"
DFA:   START → CURRENCY_SYMBOL → INTEGER_PART → DECIMAL_POINT → DECIMAL_PART → END
Output: "पाँच सौ रुपये पचास पैसे"
```

**Normalizer**: Splits into rupee and paise parts, converts each to Hindi words, appends singular/plural unit names from the resource file.

### 2. Cardinal Numbers

**DFA**: Matches pure digit sequences (`\d+`).

```
Input: "125000"
DFA:   START → DIGIT → DIGIT → ... → END
Output: "एक लाख पच्चीस हज़ार"
```

**Normalizer**: Uses the Indian numbering system — crores (10⁷), lakhs (10⁵), thousands (10³), hundreds (10²), then tens/ones with special compound forms for 11-99.

### 3. Units (Measurement)

**DFA**: Matches `<number><unit_abbreviation>` (e.g. `5kg`, `25°C`, `500MB`). Supports 40+ unit abbreviations including Hindi ones (किमी, किग्रा).

```
Input: "5kg"
DFA:   START → NUMBER → UNIT_SYMBOL → END
Output: "पाँच किलोग्राम"
```

**Normalizer**: Converts the number to Hindi words, looks up the unit abbreviation in `hi-IN.json → units`.

### 4. Date

**DFA**: Matches `DD/MM/YYYY`, `DD-MM-YYYY`, or `DD.MM.YYYY` with day (1-31) and month (1-12) validation.

```
Input: "15/08/2024"
DFA:   START → DAY → SEPARATOR → MONTH → SEPARATOR → YEAR → END
Output: "पंद्रह अगस्त दो हज़ार चौबीस"
```

**Normalizer**: Converts day and year to Hindi number words, looks up month name from `hi-IN.json → dates → months`.

### 5. Time

**DFA**: Matches `HH:MM`, `HH:MM:SS`, and optional `AM/PM` suffix. Validates hour (0-23), minute (0-59), second (0-59).

```
Input: "10:30"
DFA:   START → HOUR → COLON → MINUTE → END
Output: "दस बजकर तीस मिनट"

Input: "2:00"       → "दो बजे"          (exact hour)
Input: "10:30:15"   → "दस बजकर तीस मिनट पंद्रह सेकंड"
Input: "10:30 AM"   → "सुबह दस बजकर तीस मिनट"
```

**Normalizer**: Uses time-specific words from `hi-IN.json → time` (बजे, बजकर, मिनट, सेकंड) and AM/PM → सुबह/दोपहर/शाम/रात mapping.

### 6. Ordinal Numbers

**DFA**: Matches digits followed by English suffixes (`st`, `nd`, `rd`, `th`) or Hindi suffixes (`ला`, `रा`, `था`, `वाँ`).

```
Input: "5th"
DFA:   START → DIGIT → ORDINAL_SUFFIX → END
Output: "पाँचवाँ"

Input: "1st" → "पहला"
Input: "2nd" → "दूसरा"
Input: "3रा" → "तीसरा"
```

**Normalizer**: Direct lookup for numbers 1-20 (which have special Hindi forms), generic `<number>वाँ` suffix for larger numbers.

### 7. Named Entity (Abbreviation Expansion)

**DFA**: Matches tokens against a known lookup table of abbreviations and titles loaded from `hi-IN.json → named_entities → abbreviations`.

```
Input: "डॉ."
DFA:   START → ENTITY_MATCH → END
Output: "डॉक्टर"
```

**Normalizer**: Direct dictionary lookup. Supports Hindi titles (डॉ., श्री, प्रो.), English titles (Dr., Mr., Prof.), and party abbreviations (भा.ज.पा., कां.).

> **Note**: This is **rule-based abbreviation expansion only**, not ML-based Named Entity Recognition. It is deterministic and fast.

---

## 📝 Usage Examples

### Single Category
```
Input:  "मेरे पास ₹500 हैं"            [currency]
Output: "मेरे पास पाँच सौ रुपये हैं"

Input:  "दूरी 10km है"                   [unit]
Output: "दूरी दस किलोमीटर है"

Input:  "स्वतंत्रता दिवस 15/08/2024 है"  [date]
Output: "स्वतंत्रता दिवस पंद्रह अगस्त दो हज़ार चौबीस है"
```

### All Categories Combined
```
Input:  "डॉ. शर्मा ने 15/08/2024 को 10:30 पर ₹500 में 5kg चावल 1st बार ख़रीदा"
Output: "डॉक्टर शर्मा ने पंद्रह अगस्त दो हज़ार चौबीस को दस बजकर तीस मिनट पर
         पाँच सौ रुपये में पाँच किलोग्राम चावल पहला बार ख़रीदा"

DFA Matches:
  NAMED_ENTITY: डॉ.       → START → ENTITY_MATCH → END
  DATE:         15/08/2024 → START → DAY → SEP → MONTH → SEP → YEAR → END
  TIME:         10:30      → START → HOUR → COLON → MINUTE → END
  CURRENCY:     ₹500       → START → CURRENCY_SYMBOL → INTEGER_PART → END
  UNIT:         5kg        → START → NUMBER → UNIT_SYMBOL → END
  ORDINAL:      1st        → START → DIGIT → ORDINAL_SUFFIX → END
```

---

## 🌐 Adding Support for a New Language

The framework is designed so that **adding a new language requires only one new JSON file**. No Python code changes are needed.

### Step-by-Step Guide

#### Step 1: Create the resource file

Create a new file at `backend/resources/<language-code>.json`. Use the [BCP 47 language tag](https://en.wikipedia.org/wiki/IETF_language_tag) format (e.g., `ta-IN` for Tamil, `te-IN` for Telugu, `bn-IN` for Bengali).

```bash
cp backend/resources/hi-IN.json backend/resources/ta-IN.json
```

#### Step 2: Fill in all sections

The resource file has **8 required sections**. Here is the complete template with a Tamil (`ta-IN`) example:

```json
{
  "language": "ta-IN",
  "language_name": "Tamil",

  "numbers": {
    "ones": {
      "0": "பூஜ்ஜியம்",
      "1": "ஒன்று",
      "2": "இரண்டு",
      "3": "மூன்று",
      "4": "நான்கு",
      "5": "ஐந்து",
      "6": "ஆறு",
      "7": "ஏழு",
      "8": "எட்டு",
      "9": "ஒன்பது"
    },
    "tens": {
      "10": "பத்து",
      "11": "பதினொன்று",
      "20": "இருபது",
      "30": "முப்பது",
      "...": "..."
    },
    "scales": {
      "hundred": "நூறு",
      "thousand": "ஆயிரம்",
      "lakh": "லட்சம்",
      "crore": "கோடி"
    }
  },

  "currency": {
    "symbol": "₹",
    "code": "INR",
    "main_unit": {
      "singular": "ரூபாய்",
      "plural": "ரூபாய்"
    },
    "sub_unit": {
      "singular": "பைசா",
      "plural": "பைசா"
    }
  },

  "units": {
    "kg": "கிலோகிராம்",
    "km": "கிலோமீட்டர்",
    "ml": "மில்லிலிட்டர்",
    "°C": "டிகிரி செல்சியஸ்",
    "...": "... (add all units you need)"
  },

  "dates": {
    "months": {
      "1": "ஜனவரி",
      "2": "பிப்ரவரி",
      "3": "மார்ச்",
      "4": "ஏப்ரல்",
      "5": "மே",
      "6": "ஜூன்",
      "7": "ஜூலை",
      "8": "ஆகஸ்ட்",
      "9": "செப்டம்பர்",
      "10": "அக்டோபர்",
      "11": "நவம்பர்",
      "12": "டிசம்பர்"
    },
    "connectors": {
      "of": "அன்று",
      "year": "ஆண்டு"
    }
  },

  "time": {
    "hour_marker": "மணி",
    "hour_minute_connector": "மணி",
    "minute_word": "நிமிடம்",
    "second_word": "வினாடி",
    "periods": {
      "AM": "காலை",
      "PM_afternoon": "மதியம்",
      "PM_evening": "மாலை",
      "PM_night": "இரவு"
    }
  },

  "ordinals": {
    "mapping": {
      "1": "முதலாவது",
      "2": "இரண்டாவது",
      "3": "மூன்றாவது",
      "...": "..."
    },
    "generic_suffix": "ஆவது"
  },

  "named_entities": {
    "abbreviations": {
      "Dr.": "டாக்டர்",
      "Mr.": "திரு",
      "Mrs.": "திருமதி",
      "...": "... (add language-specific titles)"
    }
  },

  "grammar_rules": {
    "number_gender": "neutral",
    "currency_gender": "neutral"
  }
}
```

#### Step 3: Use the new language

Pass the language code when starting the engine or through the API:

**Python:**
```python
engine = NormalizationEngine(language='ta-IN')
result = engine.normalize("தொகை ₹500", ['currency'])
```

**API (POST /api/normalize):**
```json
{
  "text": "தொகை ₹500",
  "categories": ["currency"],
  "language": "ta-IN"
}
```

**Frontend:** Select the language from the dropdown (the UI already has a language selector).

#### Step 4: (Optional) Add language-specific DFA patterns

If the new language uses **different currency symbols or unit abbreviations**, add them to:
- `dfa_engine.py → CurrencyDFA.currency_symbols` (for new currency symbols)
- `dfa_engine.py → UnitDFA.UNIT_PATTERN` (for language-specific unit abbreviations)

For most Indian languages sharing ₹ and standard metric units, **no code changes are needed**.

### Checklist for a New Language

| Section | Keys to fill | Count (Hindi) |
|---------|-------------|---------------|
| `numbers.ones` | 0–9 | 10 words |
| `numbers.tens` | 10–99 (compound forms) | ~30 words |
| `numbers.scales` | hundred, thousand, lakh, crore | 4 words |
| `currency` | symbol, main_unit, sub_unit | 5 values |
| `units` | All unit abbreviations → spoken form | ~40 mappings |
| `dates.months` | 1–12 month names | 12 words |
| `time` | hour_marker, connectors, periods | ~8 words |
| `ordinals.mapping` | 1–20 ordinal forms + generic suffix | 21 values |
| `named_entities.abbreviations` | Titles & abbreviations | ~22 mappings |

**Total**: ~150 entries per language.

---

## 🧪 Test Cases

The project includes **22 comprehensive test cases** across all 7 categories:

| # | Category | Input | Expected Behavior |
|---|----------|-------|-------------------|
| 1 | Currency | `₹500` | Simple rupee conversion |
| 2 | Currency | `₹500.50` | Rupee + paise handling |
| 3 | Currency | `₹125000` | Large amount (lakhs) |
| 4 | Cardinal | `25` | Basic number-to-words |
| 5 | Cardinal | `5000000` | Lakhs/crores |
| 6 | Unit | `5kg` | Weight unit |
| 7 | Unit | `10km` | Distance unit |
| 8 | Unit | `100ml` | Volume unit |
| 9 | Unit | `25°C` | Temperature unit |
| 10 | Unit | `500MB` | Data unit |
| 11 | Date | `15/08/2024` | Slash-separated date |
| 12 | Date | `01-01-2025` | Dash-separated date |
| 13 | Date | `26.01.2026` | Dot-separated date |
| 14 | Time | `10:30` | Simple time |
| 15 | Time | `14:45` | 24-hour format |
| 16 | Time | `10:30:15` | Time with seconds |
| 17 | Time | `2:00` | Exact hour |
| 18 | Ordinal | `1st` | First (special form) |
| 19 | Ordinal | `5th` | Regular ordinal |
| 20 | Ordinal | `3रा` | Hindi suffix |
| 21 | Named Entity | `डॉ.`, `श्री`, `Dr.` | Title expansion |
| 22 | Mixed | All 7 in one sentence | Priority-ordered detection |

---

## 🎓 Educational Value

This project demonstrates:

- **DFA Theory**: Practical application of finite automata for pattern matching
- **Rule-Based NLP**: Deterministic text processing without ML models
- **Indian Numbering**: Proper handling of lakhs and crores
- **SSML Standards**: Speech synthesis markup for TTS engines
- **Modular Design**: Clean, extensible architecture patterns
- **Language Abstraction**: Resource-driven localization — one JSON file per language

## 🚧 Future Enhancements

- [ ] Phone number normalization (e.g., "9876543210" → digit-by-digit reading)
- [ ] Fraction support (e.g., "½" → "आधा", "¼" → "एक चौथाई")
- [ ] Support for more Indian languages (Tamil, Telugu, Kannada, Bengali, Marathi)
- [ ] Roman numeral conversion
- [ ] Percentage handling (e.g., "50%" → "पचास प्रतिशत")


---

**Note**: This is a deterministic, rule-based system. For production deployment, consider adding:
- Comprehensive error handling and logging
- Performance optimization and caching
- API rate limiting and security measures
- Edge case handling for all categories
