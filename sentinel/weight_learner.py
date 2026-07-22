import os
import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from typing import Dict

class WeightLearner:
    """
    Learns non-negative normalized weights [w1, w2, w3, w4, w5] summing to 1.0
    for features [CD, PV, TR, ST, ML] using Set A training traces.
    """
    
    def __init__(self):
        # Default baseline weights if not trained or file doesn't exist
        self.weights = {
            "w1_CD": 0.2,
            "w2_PV": 0.2,
            "w3_TR": 0.2,
            "w4_ST": 0.2,
            "w5_ML": 0.2
        }
        self.feature_names = ["w1_CD", "w2_PV", "w3_TR", "w4_ST", "w5_ML"]
        self.intercept = 0.0
        
    def train(self, feature_matrix: np.ndarray, labels: np.ndarray) -> Dict[str, float]:
        """Alias for fit."""
        return self.fit(feature_matrix, labels)

    def get_weights(self) -> Dict[str, float]:
        """Return the dictionary of current feature weights."""
        return self.weights

    def predict_combined_risk(self, feature_vector: np.ndarray) -> float:
        """
        Compute weighted sum of [CD, PV, TR, ST, ML] features.
        """
        w = list(self.weights.values())
        return float(np.dot(feature_vector, w))

    def fit(self, feature_matrix: np.ndarray, labels: np.ndarray) -> Dict[str, float]:
        """
        Fit Logistic Regression on the feature matrix [CD, PV, TR, ST, ML] and labels
        to learn the normalized weights.
        
        Args:
            feature_matrix (np.ndarray): The input features array.
            labels (np.ndarray): The target labels.
            
        Returns:
            Dict[str, float]: A dictionary containing the learned weights.
        """
        # Fit logistic regression to learn the feature importance (weights)
        clf = LogisticRegression(random_state=42, max_iter=1000)
        clf.fit(feature_matrix, labels)
        
        self.intercept = float(clf.intercept_[0])
        coef = clf.coef_[0]
        
        # Ensure weights are non-negative
        coef = np.maximum(0, coef)
        
        # Fallback to uniform if all coefficients are zero or less
        if np.sum(coef) == 0:
            coef = np.ones(len(self.feature_names))
            
        # Normalize weights so they sum to 1.0
        coef = coef / np.sum(coef)
        
        # Update the weights dictionary
        for i, name in enumerate(self.feature_names):
            self.weights[name] = float(coef[i])
            
        return self.weights
        
    def save_weights(self, path: str) -> None:
        """
        Save learned weights to a JSON file (e.g., data/models/frozen_weights.json).
        
        Args:
            path (str): The file path to save the weights to.
        """
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.weights, f, indent=4)
            
    def load_weights(self, path: str) -> Dict[str, float]:
        """
        Load frozen weights from a JSON file. 
        Includes default baseline weights if file does not exist.
        
        Args:
            path (str): The file path to load the weights from.
            
        Returns:
            Dict[str, float]: The loaded or default weights.
        """
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                self.weights = json.load(f)
        return self.weights
