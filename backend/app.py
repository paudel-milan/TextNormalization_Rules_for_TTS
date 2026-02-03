"""
Flask Backend API for Hindi Text Normalization
Handles normalization requests and returns normalized text, SSML, and DFA info
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from normalization_engine import NormalizationEngine
import traceback

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize the normalization engine with Hindi language
engine = NormalizationEngine(language='hi-IN')


@app.route('/api/normalize', methods=['POST'])
def normalize_text():
    """
    API endpoint for text normalization
    
    Expected JSON payload:
    {
        "text": "Hindi text to normalize",
        "categories": ["currency", "cardinal"]
    }
    
    Returns:
    {
        "normalized_text": "Normalized Hindi text",
        "ssml": "SSML output",
        "dfa_info": [...],
        "success": true
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: text'
            }), 400
        
        input_text = data['text']
        categories = data.get('categories', ['currency', 'cardinal'])
        
        # Process the text through normalization engine
        result = engine.normalize(input_text, categories)
        
        return jsonify({
            'success': True,
            'normalized_text': result['normalized_text'],
            'ssml': result['ssml'],
            'dfa_info': result['dfa_info']
        })
        
    except Exception as e:
        print(f"Error during normalization: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'language': 'hi-IN',
        'available_categories': ['currency', 'cardinal']
    })


if __name__ == '__main__':
    print("Starting Hindi Text Normalization API...")
    print("Available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
