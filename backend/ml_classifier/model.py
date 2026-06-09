"""
ML Category Classifier — Pluggable model wrapper.

Supports multiple sklearn-compatible classifiers with a unified interface.
Designed for easy swap to IndicBERT/XLM-R transformer models later.
"""

import os
import numpy as np
from pathlib import Path

try:
    import joblib
except ImportError:
    joblib = None

try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.svm import SVC
    from sklearn.neural_network import MLPClassifier
    from sklearn.feature_extraction import DictVectorizer
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    # pyrefly: ignore [missing-import]
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False


# Where trained models are stored
MODELS_DIR = Path(__file__).resolve().parent / 'models'


class CategoryClassifier:
    """
    Pluggable ML classifier for token category prediction.

    Supports:
        - logistic_regression (default, lightweight)
        - random_forest
        - xgboost (requires xgboost package)
        - gradient_boosting
        - svm
        - mlp

    The interface is designed so that a TransformerClassifier
    (IndicBERT/XLM-R) can be a drop-in replacement.
    """

    CATEGORIES = [
        'currency', 'cardinal', 'ordinal', 'date', 'time',
        'phone_number', 'unit', 'named_entity', 'text',
    ]

    SUPPORTED_MODELS = [
        'logistic_regression', 'random_forest', 'xgboost',
        'gradient_boosting', 'svm', 'mlp',
    ]

    def __init__(self, model_type='logistic_regression'):
        if not HAS_SKLEARN:
            raise ImportError(
                "scikit-learn is required for ML classification. "
                "Install it with: pip install scikit-learn"
            )

        self.model_type = model_type
        self.model = self._create_model(model_type)
        self.feature_names = []
        self.vectorizer = None
        self.is_trained = False

    def _create_model(self, model_type):
        """Create the underlying sklearn model."""
        if model_type == 'logistic_regression':
            return LogisticRegression(
                max_iter=1000,
                multi_class='multinomial',
                solver='lbfgs',
                class_weight='balanced',
                random_state=42,
            )
        elif model_type == 'random_forest':
            return RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                class_weight='balanced',
                random_state=42,
            )
        elif model_type == 'gradient_boosting':
            return GradientBoostingClassifier(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.1,
                random_state=42,
            )
        elif model_type == 'svm':
            return SVC(
                kernel='linear',
                C=1.0,
                probability=True,
                class_weight='balanced',
                random_state=42,
            )
        elif model_type == 'mlp':
            return MLPClassifier(
                hidden_layer_sizes=(128, 64),
                max_iter=1000,
                alpha=0.01,
                learning_rate_init=0.005,
                random_state=42,
                early_stopping=True,
            )
        elif model_type == 'xgboost':
            if not HAS_XGBOOST:
                raise ImportError(
                    "xgboost is required for XGBoost classifier. "
                    "Install it with: pip install xgboost"
                )
            return XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                use_label_encoder=False,
                eval_metric='mlogloss',
            )
        else:
            raise ValueError(
                f"Unsupported model type '{model_type}'. "
                f"Choose from: {self.SUPPORTED_MODELS}"
            )

    def train(self, X, y, feature_names=None):
        """
        Train the classifier.

        Args:
            X: Feature matrix (np.ndarray or list of dicts)
            y: Category labels (list of str)
            feature_names: Optional list of feature names for interpretability
        """
        if isinstance(X, list) and len(X) > 0 and isinstance(X[0], dict):
            self.vectorizer = DictVectorizer(sparse=False)
            X = self.vectorizer.fit_transform(X)
            self.feature_names = self.vectorizer.get_feature_names_out().tolist()
        elif feature_names:
            self.feature_names = feature_names

        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, X):
        """
        Predict categories with confidence scores.

        Args:
            X: Feature matrix (np.ndarray or list of dicts)

        Returns:
            List of dicts: [{'category': str, 'confidence': float, 'all_scores': dict}]
        """
        if not self.is_trained:
            raise RuntimeError("Model has not been trained yet. Call train() first.")

        if isinstance(X, list) and len(X) > 0 and isinstance(X[0], dict):
            if self.vectorizer:
                X = self.vectorizer.transform(X)
            else:
                feature_names = self.feature_names or sorted(X[0].keys())
                X = np.array([[fd.get(name, 0.0) for name in feature_names] for fd in X])

        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        classes = self.model.classes_

        results = []
        for i, pred in enumerate(predictions):
            prob_dict = {
                cls: float(probabilities[i][j])
                for j, cls in enumerate(classes)
            }
            results.append({
                'category': str(pred),
                'confidence': float(max(probabilities[i])),
                'all_scores': prob_dict,
            })

        return results

    def predict_single(self, features_dict, feature_names=None):
        """
        Predict category for a single token's features.

        Args:
            features_dict: Dict of feature_name -> value
            feature_names: Ordered list of feature names (uses self.feature_names if None)

        Returns:
            dict: {'category': str, 'confidence': float, 'all_scores': dict}
        """
        if self.vectorizer:
            return self.predict([features_dict])[0]

        names = feature_names or self.feature_names
        if not names:
            names = sorted(features_dict.keys())

        X = np.array([[features_dict.get(name, 0.0) for name in names]])
        return self.predict(X)[0]

    def save(self, filepath=None, language='hi-IN'):
        """
        Save trained model to disk.

        Args:
            filepath: Explicit path, or auto-generated from language
            language: Language code for auto-generated filename
        """
        if not joblib:
            raise ImportError("joblib is required to save models.")

        if filepath is None:
            MODELS_DIR.mkdir(parents=True, exist_ok=True)
            filepath = MODELS_DIR / f'{language}_{self.model_type}.pkl'

        data = {
            'model': self.model,
            'model_type': self.model_type,
            'feature_names': self.feature_names,
            'categories': self.CATEGORIES,
            'vectorizer': self.vectorizer,
        }
        joblib.dump(data, filepath)
        return str(filepath)

    def load(self, filepath=None, language='hi-IN'):
        """
        Load trained model from disk.

        Args:
            filepath: Explicit path, or auto-detected from language
            language: Language code for auto-detection
        """
        if not joblib:
            raise ImportError("joblib is required to load models.")

        if filepath is None:
            filepath = MODELS_DIR / f'{language}_{self.model_type}.pkl'

        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"No trained model found at {filepath}. "
                f"Train one with: python -m ml_classifier.trainer --language {language}"
            )

        data = joblib.load(filepath)
        self.model = data['model']
        self.model_type = data['model_type']
        self.feature_names = data['feature_names']
        self.vectorizer = data.get('vectorizer')
        self.is_trained = True

    @classmethod
    def get_available_models(cls, language='hi-IN'):
        """List trained models available for a language."""
        available = []
        for model_type in cls.SUPPORTED_MODELS:
            path = MODELS_DIR / f'{language}_{model_type}.pkl'
            if path.exists():
                available.append(model_type)
        return available

    def get_feature_importance(self):
        """
        Get feature importance rankings (for interpretability).

        Returns:
            List of (feature_name, importance) sorted by importance
        """
        if not self.is_trained or not self.feature_names:
            return []

        if self.model_type == 'logistic_regression':
            # Average absolute coefficient across all classes
            importances = np.mean(np.abs(self.model.coef_), axis=0)
        elif self.model_type in ('random_forest', 'xgboost'):
            importances = self.model.feature_importances_
        else:
            return []

        ranked = sorted(
            zip(self.feature_names, importances),
            key=lambda x: x[1],
            reverse=True,
        )
        return ranked


class TransformerClassifier:
    """
    Placeholder for future transformer-based classifier.
    Drop-in replacement using IndicBERT or XLM-R.

    NOT YET IMPLEMENTED — included as an architectural placeholder
    to show the plug-in design.
    """

    def __init__(self, model_name='ai4bharat/indic-bert'):
        self.model_name = model_name
        self.is_trained = False
        raise NotImplementedError(
            "TransformerClassifier is a future extension. "
            "Use CategoryClassifier with sklearn models for now."
        )

    def train(self, X, y, feature_names=None):
        raise NotImplementedError

    def predict(self, X):
        raise NotImplementedError

    def save(self, filepath=None, language='hi-IN'):
        raise NotImplementedError

    def load(self, filepath=None, language='hi-IN'):
        raise NotImplementedError
