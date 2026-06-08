# 🔊 Hybrid Text Normalization for TTS — What's New

## Overview

The Text Normalization system has been enhanced with an **ML-based Category Detection** module, creating a **hybrid architecture** where:

- **ML classifies token categories** (currency, date, time, cardinal, ordinal, unit, named entity, phone number)
- **Existing rule engine normalizes** the detected tokens and generates SSML

This is an **additive enhancement** — the existing Manual Mode is 100% preserved.

---

## 🆕 What Changed

### New Architecture

```
Input Text
    ↓
┌─────────────────────────────────────────┐
│  Step 1: Tokenize                       │
│  Step 2: Rule-Based Detection (DFA)     │ ← Existing DFAs
│  Step 3: ML Classification (sklearn)    │ ← NEW
│  Step 4: Combine Predictions            │ ← NEW (hybrid logic)
│  Step 5: Normalize + SSML Generation    │ ← Existing normalizers
└─────────────────────────────────────────┘
    ↓
Normalized Text + SSML + Token Details
```

### New Files & Folders

```
backend/
├── ml_classifier/              ← NEW: ML classification module
│   ├── feature_extractor.py    ← Token feature extraction (30+ features)
│   ├── model.py                ← Pluggable classifier (LogReg/RF/XGBoost)
│   ├── trainer.py              ← Training pipeline with CLI
│   └── models/                 ← Saved trained models (.pkl)
├── rule_engine/                ← NEW: Rule detector wrapper
│   └── detector.py             ← Unified DFA interface
├── engine/
│   └── hybrid_engine.py        ← NEW: 5-step hybrid pipeline
├── training_data/              ← NEW: Labelled training samples
│   ├── hi-IN_training.json     ← Hindi (60+ samples)
│   ├── ne-NP_training.json     ← Nepali (35+ samples)
│   └── ta-IN_training.json     ← Tamil (34+ samples)
```

### New API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auto-normalize` | POST | Hybrid auto-detect normalization |
| `/api/train` | POST | Train ML model for a language |
| `/api/model-status` | GET | Check trained model availability |
| `/api/normalize` | POST | **Unchanged** — Manual mode |
| `/api/health` | GET | **Unchanged** — Health check |

### Frontend Changes

- **Mode Toggle**: Switch between Manual Mode and Auto Detect Mode
- **Model Status**: Shows if ML model is trained for the selected language
- **Train Button**: One-click model training from the UI
- **Token Detection Table**: Shows per-token breakdown with rule/ML/final categories
- **Confidence Bars**: Visual confidence indicators
- **Pipeline Summary**: Stats for total tokens, detected tokens, categories found

---

## 🚀 How to Set Up & See the Changes

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs the new dependencies: `scikit-learn`, `numpy`, `joblib`

### Step 2: Train the ML Model

**Option A: Command Line**
```bash
cd backend
python -m ml_classifier.trainer --language hi-IN --model logistic_regression
```

**Option B: API Call**
```bash
curl -X POST http://localhost:5000/api/train \
  -H "Content-Type: application/json" \
  -d '{"language": "hi-IN", "model_type": "logistic_regression"}'
```

**Option C: From the UI** (after starting the backend)
1. Switch to "Auto Detect" mode
2. Click the "Train Model" button

Train all languages:
```bash
cd backend
python -m ml_classifier.trainer --language hi-IN
python -m ml_classifier.trainer --language ne-NP
python -m ml_classifier.trainer --language ta-IN
```

### Step 3: Start the Backend

```bash
cd backend
python app.py
```

You should see:
```
Starting Text Normalization API (Hybrid ML + Rules)...
Available languages: hi-IN, ne-NP, ta-IN
Modes: Manual | Auto Detect (Hybrid ML + Rules)
Available at: http://localhost:5000
```

### Step 4: Open the Frontend

Open `frontend/index.html` in your browser.

---

## 🧪 Testing the New Features

### Test Manual Mode (Unchanged)

1. Select "Manual Mode" (default)
2. Select Language: Hindi (hi-IN)
3. Check categories: Currency, Cardinal, Date
4. Enter: `उसने बाजार से ₹500 की किताबें खरीदीं`
5. Click "Generate Normalization"
6. Verify: Same output as before

### Test Auto Detect Mode

1. Switch to "Auto Detect" mode
2. Select Language: Hindi (hi-IN)
3. Enter: `डॉ. शर्मा ने 15/08/2024 को सुबह 10:30 बजे ₹500 में 5kg चावल ख़रीदा`
4. Click "Generate Normalization"
5. Verify the Token Detection Table shows:

| Token | Rule Category | ML Category | Final Category | Confidence |
|-------|--------------|-------------|----------------|------------|
| डॉ. | named_entity | named_entity | named_entity | 90% |
| शर्मा | text | text | text | 0% |
| ने | text | text | text | 0% |
| 15/08/2024 | date | date | date | 90% |
| को | text | text | text | 0% |
| सुबह | text | text | text | 0% |
| 10:30 | time | time | time | 90% |
| बजे | text | text | text | 0% |
| ₹500 | currency | currency | currency | 90% |
| में | text | text | text | 0% |
| 5kg | unit | unit | unit | 90% |
| चावल | text | text | text | 0% |
| ख़रीदा | text | text | text | 0% |

### Test API Directly

```bash
# Auto Detect
curl -X POST http://localhost:5000/api/auto-normalize \
  -H "Content-Type: application/json" \
  -d '{"text": "₹500 में 5kg चावल", "language": "hi-IN"}'

# Check model status
curl http://localhost:5000/api/model-status

# Manual mode (unchanged)
curl -X POST http://localhost:5000/api/normalize \
  -H "Content-Type: application/json" \
  -d '{"text": "₹500", "categories": ["currency"], "language": "hi-IN"}'
```

---

## ➕ Adding New Languages

1. **Create language resource**: `backend/resources/{lang-code}.json`
2. **Create training data**: `backend/training_data/{lang-code}_training.json`
3. **Train the model**: `python -m ml_classifier.trainer --language {lang-code}`
4. **Add to frontend dropdown** in `frontend/index.html`

### Training Data Format

```json
{
    "language": "xx-XX",
    "version": "1.0",
    "samples": [
        {
            "text": "Full sentence",
            "tokens": [
                {"token": "word", "category": "currency|cardinal|date|time|unit|ordinal|named_entity|text"}
            ]
        }
    ]
}
```

---

## 🔄 Upgrading the ML Model

### Current: Lightweight Models
- Logistic Regression (default, fast, interpretable)
- Random Forest
- XGBoost (needs `pip install xgboost`)

### Future: Transformer Models
The architecture supports drop-in replacement with:
- **IndicBERT** (`ai4bharat/indic-bert`)
- **XLM-R** (`xlm-roberta-base`)

The `TransformerClassifier` placeholder exists in `ml_classifier/model.py`.

---

## 📁 Complete Project Structure

```
samsumg_TN_TTS/
├── backend/
│   ├── app.py                          ← Flask API (4 endpoints)
│   ├── requirements.txt                ← Dependencies
│   ├── engine/
│   │   ├── normalization_engine.py     ← Original engine (unchanged)
│   │   └── hybrid_engine.py            ← NEW: Hybrid pipeline
│   ├── ml_classifier/                  ← NEW: ML module
│   │   ├── feature_extractor.py
│   │   ├── model.py
│   │   ├── trainer.py
│   │   └── models/                     ← Saved models
│   ├── rule_engine/                    ← NEW: Rule wrapper
│   │   └── detector.py
│   ├── training_data/                  ← NEW: Training samples
│   │   ├── hi-IN_training.json
│   │   ├── ne-NP_training.json
│   │   └── ta-IN_training.json
│   ├── dfa/                            ← Unchanged
│   ├── normalizers/                    ← Unchanged
│   ├── ssml/                           ← Unchanged
│   ├── resources/                      ← Unchanged
│   └── tests/                          ← Unchanged
├── frontend/
│   ├── index.html                      ← Updated with mode toggle
│   ├── script.js                       ← Updated with auto-detect logic
│   └── styles.css                      ← Updated with new UI components
├── README.md                           ← Original readme
└── README_new.md                       ← This file
```
