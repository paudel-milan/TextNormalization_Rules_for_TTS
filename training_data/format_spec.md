# Training Data Format Specification

## File Naming
Each language has its own training data file:
- `hi-IN_training.json` — Hindi
- `ne-NP_training.json` — Nepali
- `ta-IN_training.json` — Tamil

## JSON Structure

```json
{
    "language": "hi-IN",
    "version": "1.0",
    "samples": [
        {
            "text": "Full sentence as input text",
            "tokens": [
                {"token": "word1", "category": "text"},
                {"token": "word2", "category": "currency"},
                ...
            ]
        }
    ]
}
```

## Rules
1. `tokens` must align with `text.split()` — same count, same order
2. Each token gets exactly one category label
3. Valid categories: `currency`, `cardinal`, `ordinal`, `date`, `time`, `phone_number`, `unit`, `named_entity`, `text`
4. Use `text` for any token that doesn't belong to a special category

## Adding New Training Data
1. Add new sample objects to the `samples` array
2. Re-train the model: `python -m ml_classifier.trainer --language hi-IN`
3. The new model replaces the old one automatically

## Adding New Languages
1. Create a new file: `{language-code}_training.json`
2. Follow the same JSON structure
3. Train: `python -m ml_classifier.trainer --language {language-code}`
