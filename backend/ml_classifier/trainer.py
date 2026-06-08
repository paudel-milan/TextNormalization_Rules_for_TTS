"""
Model Training Pipeline for ML-based Category Classification.

Loads training data from JSON files, extracts features, trains
a classifier, evaluates it, and saves the trained model.

Usage:
    python -m ml_classifier.trainer --language hi-IN --model logistic_regression
"""

import json
import argparse
import sys
from pathlib import Path

import numpy as np

from .feature_extractor import FeatureExtractor
from .model import CategoryClassifier


# Directory where training data JSON files live
TRAINING_DATA_DIR = Path(__file__).resolve().parent.parent / 'training_data'


class ModelTrainer:
    """
    End-to-end training pipeline:
    1. Load labelled training data from JSON
    2. Extract features per token
    3. Train classifier
    4. Evaluate with train/test split
    5. Save trained model
    """

    def __init__(self, language='hi-IN', model_type='logistic_regression'):
        self.language = language
        self.model_type = model_type
        self.feature_extractor = FeatureExtractor()
        self.classifier = CategoryClassifier(model_type=model_type)

    def load_training_data(self):
        """
        Load training samples from the JSON file for this language.

        Returns:
            list of sample dicts from the JSON 'samples' array
        """
        filepath = TRAINING_DATA_DIR / f'{self.language}_training.json'
        if not filepath.exists():
            raise FileNotFoundError(
                f"Training data not found at {filepath}. "
                f"Create it following the format in training_data/format_spec.md"
            )

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        samples = data.get('samples', [])
        print(f"Loaded {len(samples)} training samples for {self.language}")
        return samples

    def prepare_features(self, samples):
        """
        Convert training samples into feature matrix + labels.

        Args:
            samples: List of sample dicts with 'text' and 'tokens' fields

        Returns:
            (X, y, feature_names): feature matrix, labels, feature name list
        """
        all_features = []
        all_labels = []

        for sample in samples:
            text = sample['text']
            token_annotations = sample['tokens']
            words = text.split()

            # Align annotations with words
            for i, annotation in enumerate(token_annotations):
                token = annotation['token']
                category = annotation['category']

                prev_word = words[i - 1] if i > 0 and i < len(words) else ''
                next_word = words[i + 1] if i + 1 < len(words) else ''

                features = self.feature_extractor.extract_single(
                    token, prev_word, next_word
                )
                all_features.append(features)
                all_labels.append(category)

        X, feature_names = self.feature_extractor.features_to_matrix(all_features)
        y = np.array(all_labels)

        print(f"Prepared {len(all_labels)} token samples with {len(feature_names)} features")
        print(f"Category distribution:")
        for cat in sorted(set(all_labels)):
            count = all_labels.count(cat)
            print(f"  {cat}: {count} ({100 * count / len(all_labels):.1f}%)")

        return X, y, feature_names

    def train_and_evaluate(self):
        """
        Full training pipeline: load → extract → split → train → evaluate.

        Returns:
            dict with training results and metrics
        """
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import classification_report, accuracy_score

        # Step 1: Load data
        samples = self.load_training_data()

        # Step 2: Extract features
        X, y, feature_names = self.prepare_features(samples)

        if len(X) < 10:
            print("WARNING: Very few training samples. Model quality will be low.")

        # Step 3: Train/test split
        if len(X) >= 20:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
        else:
            # Too few samples to split — train on all
            X_train, X_test = X, X
            y_train, y_test = y, y

        # Step 4: Train
        print(f"\nTraining {self.model_type} classifier...")
        self.classifier.train(X_train, y_train, feature_names=feature_names)

        # Step 5: Evaluate
        y_pred = self.classifier.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, zero_division=0)

        print(f"\n{'='*60}")
        print(f"Model: {self.model_type}")
        print(f"Language: {self.language}")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"{'='*60}")
        print(report)

        # Feature importance
        importance = self.classifier.get_feature_importance()
        if importance:
            print("\nTop 10 Important Features:")
            for name, score in importance[:10]:
                print(f"  {name}: {score:.4f}")

        return {
            'accuracy': accuracy,
            'report': report,
            'n_train': len(X_train),
            'n_test': len(X_test),
            'n_features': len(feature_names),
            'feature_importance': importance[:10] if importance else [],
        }

    def save_model(self):
        """Save the trained model to disk."""
        path = self.classifier.save(language=self.language)
        print(f"\nModel saved to: {path}")
        return path

    def run(self):
        """Complete pipeline: train, evaluate, save."""
        results = self.train_and_evaluate()
        model_path = self.save_model()
        results['model_path'] = model_path
        return results


def main():
    """CLI entry point for model training."""
    parser = argparse.ArgumentParser(
        description='Train ML category classifier for Text Normalization'
    )
    parser.add_argument(
        '--language', '-l',
        default='hi-IN',
        help='Language code (e.g., hi-IN, ne-NP, ta-IN)'
    )
    parser.add_argument(
        '--model', '-m',
        default='logistic_regression',
        choices=CategoryClassifier.SUPPORTED_MODELS,
        help='Model type to train'
    )

    args = parser.parse_args()

    trainer = ModelTrainer(language=args.language, model_type=args.model)
    results = trainer.run()

    print(f"\n✅ Training complete!")
    print(f"   Accuracy: {results['accuracy']:.2%}")
    print(f"   Model: {results['model_path']}")


if __name__ == '__main__':
    main()
