# Quick Start Guide

## 🚀 Running the Application

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Start Backend Server
```bash
python app.py
```
✅ Server will start at `http://localhost:5000`

### Step 3: Open Frontend
- Option A: Double-click `frontend/index.html`
- Option B: Use a local server:
  ```bash
  cd frontend
  python -m http.server 8000
  ```
  Then open `http://localhost:8000`

### Step 4: Test the System
```bash
cd backend
python test_normalization.py
```

## 📝 Example Usage

1. Open the frontend in your browser
2. Enter Hindi text: `मेरे पास ₹500 हैं और मुझे 25 किताबें चाहिए`
3. Select categories: Currency ✓, Cardinal ✓
4. Click "Generate Normalization"
5. View results:
   - Normalized: `मेरे पास पाँच सौ रुपये हैं और मुझे पच्चीस किताबें चाहिए`
   - SSML output
   - DFA state transitions

## 🎯 Key Features

- ✅ Currency normalization (₹500 → पाँच सौ रुपये)
- ✅ Decimal support (₹500.50 → पाँच सौ रुपये पचास पैसे)
- ✅ Cardinal numbers (123 → एक सौ तेईस)
- ✅ Indian numbering (125000 → एक लाख पच्चीस हज़ार)
- ✅ SSML generation for TTS
- ✅ DFA state visualization

## 📚 Documentation

- Full documentation: [README.md](file:///C:/Users/milan/OneDrive/Documents/Desktop/projects/samsumg_TN_TTS/README.md)
- Architecture details in README
- Test cases in `backend/test_normalization.py`
