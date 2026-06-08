# Multi-Language Text Normalization Engine

A rule-based text normalization engine for local languages (Hindi, Nepali), designed to be easily extensible to new languages without modifying the core logic.

## Project Structure

- `backend/`: Core normalization logic.
  - `engine/`: Orchestration and normalization pipeline.
  - `dfa/`: Finite State Automata for token detection. All patterns are now externalized.
  - `normalizers/`: Rules for converting tokens to words. Language-specific logic is parameterised via JSON.
  - `resources/`: Language-specific JSON configuration files (`hi-IN.json`, `ne-NP.json`).
  - `tests/`: Comprehensive test suite.
- `frontend/`: User interface for testing normalization.

## Adding a New Language

To add support for a new language (e.g., `mr-IN` for Marathi):

1.  Create a `backend/resources/mr-IN.json` file.
2.  Follow the structure of `hi-IN.json`.
3.  Define the following in your JSON:
    - `numbers`: Digits and scale mappings (Indian numbering system).
    - `currency`: Units and symbols.
    - `patterns`: Regex patterns for each category (date, time, currency, unit, ordinal, cardinal).
    - `rules`: Normalization rules (e.g., time period thresholds, minus word, decimal word).
    - `units`: Measurement unit expansions.
    - `dates`: Month names and connectors.
    - `ordinals`: Mapping and generic suffixes.
    - `named_entities`: Common abbreviations.

## Testing

Run the full test suite for all supported languages:

```bash
cd backend
python tests/run_all.py
```

To run language-specific tests:

```bash
python tests/test_time.py   # Defaults to Hindi
python tests/test_nepali.py # Nepali specific tests
```

## Features

- **Extensible Architecture**: No hardcoded regexes or language-specific words in the Python code.
- **Support for Multi-Language**: Seamlessly switch between languages by providing different JSON resources.
- **Robust Detection**: DFA-based detection ensures accurate tokenization.
- **Detailed SSML Generation**: Generates standard-compliant SSML for downstream TTS engines.
