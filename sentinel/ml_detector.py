import os
import joblib
import numpy as np
from typing import Any

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

from sklearn.ensemble import RandomForestClassifier

class MLDetector:
    """
    MLDetector uses an XGBoost classifier (or RandomForest fallback) to detect malicious
    activity based on structural features like execution depth, call count, 
    argument entropy, and tool transition frequency.
    """
    
    def __init__(self):
        if HAS_XGBOOST:
            self.model = xgb.XGBClassifier(eval_metric='logloss')
        else:
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            
    def extract_structural_features(self, tool_call: dict) -> list:
        """
        Extract numerical structural features from a single tool call dictionary.
        """
        step = float(tool_call.get('step', 1))
        args = str(tool_call.get('args', {}))
        arg_len = float(len(args))
        tool_name = str(tool_call.get('tool_name', ''))
        tool_hash = float(hash(tool_name) % 100) / 100.0
        source_trust = float(tool_call.get('source_trust', 1.0))
        return [step, arg_len, tool_hash, source_trust]

    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Train the classifier on the given features and labels.
        
        Args:
            X (np.ndarray): The input features array.
            y (np.ndarray): The labels array.
        """
        self.model.fit(X, y)

    def predict_risk(self, tool_call: dict) -> float:
        """
        Predict the risk probability of a single tool call.
        """
        feats = np.array([self.extract_structural_features(tool_call)])
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(feats)
            if probs.shape[1] > 1:
                return float(probs[0][1])
            return float(probs[0][0])
        return 0.0
        
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict probability for the classes.
        
        Args:
            X (np.ndarray): The input features array.
            
        Returns:
            np.ndarray: The predicted probabilities.
        """
        return self.model.predict_proba(X)
        
    def save_model(self, path: str) -> None:
        """
        Save the trained model to the specified path.
        
        Args:
            path (str): The file path where the model will be saved.
        """
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        joblib.dump(self.model, path)
        
    def load_model(self, path: str) -> None:
        """
        Load a trained model from the specified path.
        
        Args:
            path (str): The file path from where the model will be loaded.
        """
        if os.path.exists(path):
            self.model = joblib.load(path)
        else:
            raise FileNotFoundError(f"Model file not found at {path}")
