"""
ML Classifiers - Machine learning models for classification tasks
"""

from typing import Dict, Any, List, Optional
import numpy as np
from .features import FeatureExtractor
import warnings
warnings.filterwarnings('ignore')


class MLClassifiers:
    """
    Machine learning classifiers for repository analysis.
    Uses ensemble methods (Random Forest, XGBoost) for classification.
    """
    
    def __init__(self):
        self.status_classifier = None
        self.quality_predictor = None
        self.tech_stack_classifier = None
        self._models_trained = False
    
    def train_status_classifier(self, X: np.ndarray, y: np.ndarray):
        """
        Train status classifier (Active, Ongoing, Started, Slowing Down, Finished).
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Labels array (n_samples,)
        """
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train Random Forest
            self.status_classifier = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            
            self.status_classifier.fit(X_train, y_train)
            
            # Evaluate
            train_score = self.status_classifier.score(X_train, y_train)
            test_score = self.status_classifier.score(X_test, y_test)
            
            print(f"[MLClassifiers] Status Classifier - Train: {train_score:.3f}, Test: {test_score:.3f}")
            
            return self.status_classifier
            
        except ImportError:
            print("[MLClassifiers] sklearn not available, using rule-based classifier")
            return None
        except Exception as e:
            print(f"[MLClassifiers] Error training status classifier: {e}")
            return None
    
    def train_quality_predictor(self, X: np.ndarray, y: np.ndarray):
        """
        Train quality score predictor (regression, 0-100).
        
        Args:
            X: Feature matrix
            y: Quality scores (0-100)
        """
        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import train_test_split
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            self.quality_predictor = RandomForestRegressor(
                n_estimators=100,
                max_depth=12,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
            
            self.quality_predictor.fit(X_train, y_train)
            
            train_score = self.quality_predictor.score(X_train, y_train)
            test_score = self.quality_predictor.score(X_test, y_test)
            
            print(f"[MLClassifiers] Quality Predictor - Train R²: {train_score:.3f}, Test R²: {test_score:.3f}")
            
            return self.quality_predictor
            
        except ImportError:
            print("[MLClassifiers] sklearn not available")
            return None
        except Exception as e:
            print(f"[MLClassifiers] Error training quality predictor: {e}")
            return None
    
    def predict_status(self, repo: Dict[str, Any]) -> str:
        """
        Predict repository status using ML model.
        Falls back to rule-based if model not trained.
        
        Args:
            repo: Repository dict
            
        Returns:
            Status string (Active, Ongoing, etc.)
        """
        if self.status_classifier is not None:
            try:
                features = FeatureExtractor.get_feature_vector(repo)
                prediction = self.status_classifier.predict([features])[0]
                return prediction
            except Exception as e:
                print(f"[MLClassifiers] Prediction error: {e}, falling back to rules")
        
        # Fallback to rule-based
        return self._rule_based_status(repo)
    
    def predict_quality(self, repo: Dict[str, Any]) -> float:
        """
        Predict quality score using ML model.
        Falls back to rule-based scorer if model not trained.
        """
        if self.quality_predictor is not None:
            try:
                features = FeatureExtractor.get_feature_vector(repo)
                prediction = self.quality_predictor.predict([features])[0]
                return float(np.clip(prediction, 0, 100))
            except Exception as e:
                print(f"[MLClassifiers] Prediction error: {e}, falling back to scorer")
        
        # Fallback: use quality scorer
        from .quality_scorer import QualityScorer
        result = QualityScorer.calculate_quality_score(repo)
        return result["total_score"]
    
    @staticmethod
    def _rule_based_status(repo: Dict[str, Any]) -> str:
        """
        Rule-based status classification (fallback).
        """
        from datetime import datetime, timezone
        
        now = datetime.now(timezone.utc)
        
        def parse_date(date_str):
            if not date_str:
                return None
            try:
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                return None
        
        pushed_at = parse_date(repo.get("pushed_at") or repo.get("updated_at"))
        created_at = parse_date(repo.get("created_at"))
        
        if not pushed_at or not created_at:
            return "Unknown"
        
        days_since_push = (now - pushed_at).days
        days_since_creation = (now - created_at).days
        
        # Enhanced thresholds
        if repo.get("archived") or days_since_push > 180:
            return "Finished"
        elif days_since_push < 7:
            return "Active"
        elif days_since_push < 30:
            return "Ongoing"
        elif days_since_push < 90:
            return "Slowing Down"
        elif days_since_creation < 90:
            return "Started"
        else:
            return "Ongoing"
    
    def save_models(self, path: str = "backend/models"):
        """Save trained models to disk"""
        try:
            import joblib
            import os
            
            os.makedirs(path, exist_ok=True)
            
            if self.status_classifier:
                joblib.dump(self.status_classifier, f"{path}/status_classifier.pkl")
                print(f"[MLClassifiers] Saved status classifier to {path}/status_classifier.pkl")
            
            if self.quality_predictor:
                joblib.dump(self.quality_predictor, f"{path}/quality_predictor.pkl")
                print(f"[MLClassifiers] Saved quality predictor to {path}/quality_predictor.pkl")
                
        except Exception as e:
            print(f"[MLClassifiers] Error saving models: {e}")
    
    def load_models(self, path: str = "backend/models"):
        """Load trained models from disk"""
        try:
            import joblib
            import os
            
            status_path = f"{path}/status_classifier.pkl"
            quality_path = f"{path}/quality_predictor.pkl"
            
            if os.path.exists(status_path):
                self.status_classifier = joblib.load(status_path)
                print(f"[MLClassifiers] Loaded status classifier from {status_path}")
            
            if os.path.exists(quality_path):
                self.quality_predictor = joblib.load(quality_path)
                print(f"[MLClassifiers] Loaded quality predictor from {quality_path}")
            
            self._models_trained = True
            
        except Exception as e:
            print(f"[MLClassifiers] Error loading models: {e}")


# Global singleton
_ml_classifiers = None

def get_ml_classifiers() -> MLClassifiers:
    """Get global ML classifiers instance"""
    global _ml_classifiers
    if _ml_classifiers is None:
        _ml_classifiers = MLClassifiers()
        # Try to load pre-trained models
        _ml_classifiers.load_models()
    return _ml_classifiers
