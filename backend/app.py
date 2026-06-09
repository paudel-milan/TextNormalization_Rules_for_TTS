"""
Flask Backend API for Text Normalization
Supports multiple languages (hi-IN, ne-NP, etc.)
Handles normalization requests and returns normalized text, SSML, and DFA info

Endpoints:
    POST /api/normalize       — Manual mode (existing)
    POST /api/auto-normalize  — Auto Detect mode (hybrid ML + Rule)
    POST /api/train           — Train ML model for a language
    GET  /api/model-status    — Check trained model availability
    GET  /api/health          — Health check
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
_hybrid_engines = {}


def get_engine(language='hi-IN'):
    """Get or create a NormalizationEngine for the given language."""
    if language not in _engines:
        _engines[language] = NormalizationEngine(language=language)
    return _engines[language]


def get_hybrid_engine(language='hi-IN'):
    """Get or create a HybridEngine for the given language."""
    from engine.hybrid_engine import HybridEngine
    if language not in _hybrid_engines:
        _hybrid_engines[language] = HybridEngine(language=language)
    return _hybrid_engines[language]


def get_available_languages():
    """Scan resources/ directory for available language files."""
    resources_dir = Path(__file__).parent / 'resources'
    return sorted(f.stem for f in resources_dir.glob('*.json'))


# Pre-initialize default engine
get_engine('hi-IN')


@app.route('/api/normalize', methods=['POST'])
def normalize_text():
    """
    API endpoint for text normalization (Manual Mode).

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


@app.route('/api/auto-normalize', methods=['POST'])
def auto_normalize_text():
    """
    API endpoint for hybrid auto-detect normalization.

    Uses ML + Rule-based hybrid pipeline to automatically
    detect token categories and normalize text.

    Expected JSON payload:
    {
        "text": "Text to normalize",
        "language": "hi-IN"   (optional, default: hi-IN)
    }

    Returns:
    {
        "success": true,
        "normalized_text": "...",
        "ssml": "...",
        "token_details": [...],
        "pipeline_summary": {...}
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
        language = data.get('language', 'hi-IN')

        try:
            engine = get_hybrid_engine(language)
        except FileNotFoundError:
            return jsonify({
                'success': False,
                'error': f'Language "{language}" is not supported. '
                         f'Available: {get_available_languages()}'
            }), 400

        result = engine.normalize(input_text)

        return jsonify({
            'success': True,
            'normalized_text': result['normalized_text'],
            'ssml': result['ssml'],
            'token_details': result['token_details'],
            'pipeline_summary': result['pipeline_summary'],
        })

    except Exception as e:
        print(f"Error during auto-normalization: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/train', methods=['POST'])
def train_model():
    """
    Trigger ML model training for a language.

    Expected JSON payload:
    {
        "language": "hi-IN",
        "model_type": "logistic_regression"  (optional)
    }
    """
    try:
        data = request.get_json() or {}
        language = data.get('language', 'hi-IN')
        model_type = data.get('model_type', 'logistic_regression')

        from ml_classifier.trainer import ModelTrainer
        trainer = ModelTrainer(language=language, model_type=model_type)
        results = trainer.run()

        # Clear cached hybrid engine so it reloads the new model
        if language in _hybrid_engines:
            del _hybrid_engines[language]

        return jsonify({
            'success': True,
            'accuracy': results['accuracy'],
            'n_train': results['n_train'],
            'n_test': results['n_test'],
            'n_features': results['n_features'],
            'model_path': results['model_path'],
            'feature_importance': [
                {'feature': name, 'importance': round(score, 4)}
                for name, score in results.get('feature_importance', [])
            ],
        })

    except FileNotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

    except Exception as e:
        print(f"Error during training: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/model-status', methods=['GET'])
def model_status():
    """
    Check if trained ML models exist for each language.

    Query params:
        language (optional): Specific language to check

    Returns available models per language.
    """
    try:
        from ml_classifier.model import CategoryClassifier

        language = request.args.get('language')
        languages = [language] if language else get_available_languages()

        status = {}
        for lang in languages:
            available = CategoryClassifier.get_available_models(lang)
            status[lang] = {
                'has_model': len(available) > 0,
                'available_models': available,
            }

        return jsonify({
            'success': True,
            'model_status': status,
        })

    except Exception as e:
        print(f"Error checking model status: {str(e)}")
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
        'modes': ['manual', 'auto_detect'],
    })


if __name__ == '__main__':
    langs = get_available_languages()
    print(f"Starting Text Normalization API (Hybrid ML + Rules)...")
    print(f"Available languages: {', '.join(langs)}")
    print(f"Modes: Manual | Auto Detect (Hybrid ML + Rules)")
    print(f"Available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5003)
