"""
Flask Backend API for Text Normalization
Supports multiple languages (hi-IN, ne-NP, etc.)
Handles normalization requests and returns normalized text, SSML, and DFA info
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from engine import NormalizationEngine
import traceback
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Cache engines per language to avoid reloading resources each request
_engines = {}


def get_engine(language='hi-IN'):
    """Get or create a NormalizationEngine for the given language."""
    if language not in _engines:
        _engines[language] = NormalizationEngine(language=language)
    return _engines[language]


def get_available_languages():
    """Scan resources/ directory for available language files."""
    resources_dir = Path(__file__).parent / 'resources'
    return sorted(f.stem for f in resources_dir.glob('*.json'))


# Pre-initialize default engine
get_engine('hi-IN')


@app.route('/api/normalize', methods=['POST'])
def normalize_text():
    """
    API endpoint for text normalization.

    Expected JSON payload:
    {
        "text": "Text to normalize",
        "categories": ["currency", "cardinal", ...],
        "language": "hi-IN"   (optional, default: hi-IN)
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
        categories = data.get('categories', [
            'currency', 'cardinal', 'unit', 'date',
            'time', 'ordinal', 'named_entity',
        ])
        language = data.get('language', 'hi-IN')

        try:
            engine = get_engine(language)
        except FileNotFoundError:
            return jsonify({
                'success': False,
                'error': f'Language "{language}" is not supported. '
                         f'Available: {get_available_languages()}'
            }), 400

        result = engine.normalize(input_text, categories)

        return jsonify({
            'success': True,
            'normalized_text': result['normalized_text'],
            'ssml': result['ssml'],
            'dfa_info': result['dfa_info'],
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
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'available_languages': get_available_languages(),
        'available_categories': [
            'currency', 'cardinal', 'unit', 'date',
            'time', 'ordinal', 'named_entity',
        ],
    })


if __name__ == '__main__':
    langs = get_available_languages()
    print(f"Starting Text Normalization API...")
    print(f"Available languages: {', '.join(langs)}")
    print(f"Available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
