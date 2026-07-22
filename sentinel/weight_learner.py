"""
Logistic regression wrapper to learn component weights for the Sentinel Risk Index.
"""
from typing import List
import numpy as np

try:
    from sklearn.linear_model import LogisticRegression
except ImportError:
    LogisticRegression = None

class WeightLearner:
    """Learns weights w1...w5 on Set A for combining risk features."""
    
    def __init__(self) -> None:
        self.model = None
        if LogisticRegression is not None:
            self.model = LogisticRegression(fit_intercept=True)
            
        # Default weights [w1, w2, w3, w4, w5] if not trained
        self.weights = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
        self.intercept = 0.0
        
    def train(self, features: np.ndarray, labels: np.ndarray) -> None:
        """
        Trains the logistic regression model to learn optimal weights.
        
        Args:
            features: Shape (n_samples, 5) representing the 5 risk components.
            labels: Shape (n_samples,) binary labels.
        """
        if self.model is None:
            raise ImportError("scikit-learn is not installed")
            
        self.model.fit(features, labels)
        self.weights = self.model.coef_[0]
        self.intercept = self.model.intercept_[0]
        
    def get_weights(self) -> List[float]:
        """Returns the currently learned weights."""
        return self.weights.tolist()
        
    def predict_combined_risk(self, feature_vector: np.ndarray) -> float:
        """
        Computes the final risk given a feature vector using learned weights.
        
        Args:
            feature_vector: Array containing [f1, f2, f3, f4, f5].
            
        Returns:
            float: Final risk score (probability).
        """
        if self.model is not None and hasattr(self.model, 'classes_'):
            proba = self.model.predict_proba(feature_vector.reshape(1, -1))[0]
            return float(proba[1] if len(proba) > 1 else 0.0)
            
        # Fallback manual calculation if model not trained
        logit = np.dot(feature_vector, self.weights) + self.intercept
        return float(1.0 / (1.0 + np.exp(-logit)))
