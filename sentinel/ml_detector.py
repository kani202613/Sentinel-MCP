"""
XGBoost training and prediction wrapper for raw structural features.
"""
import json
from typing import Any, Dict, List
import numpy as np

try:
    import xgboost as xgb
except ImportError:
    xgb = None  # Handle gracefully if not installed yet

class MLDetector:
    """XGBoost-based detector for structural anomalies in tool traces."""
    
    def __init__(self) -> None:
        self.model = None
        if xgb is not None:
            self.model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=3,
                learning_rate=0.1,
                use_label_encoder=False,
                eval_metric='logloss'
            )
            
    def extract_structural_features(self, tool_call: Dict[str, Any]) -> List[float]:
        """
        Extracts structural features like argument depth and entropy.
        
        Args:
            tool_call: The tool call data.
            
        Returns:
            List[float]: Extracted feature vector [depth, entropy].
        """
        args = tool_call.get("arguments", {})
        
        # Feature 1: Argument structure depth
        def get_depth(d: Any, current_depth: int = 1) -> int:
            if isinstance(d, dict) and d:
                return max([get_depth(v, current_depth + 1) for v in d.values()], default=current_depth)
            elif isinstance(d, list) and d:
                return max([get_depth(item, current_depth + 1) for item in d], default=current_depth)
            return current_depth
            
        depth = float(get_depth(args))
        
        # Feature 2: Argument entropy (simple approximation using JSON string length)
        # In a real scenario, use proper Shannon entropy on string values
        args_str = json.dumps(args)
        entropy = min(len(args_str) / 1000.0, 1.0) 
        
        return [depth, entropy]

    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """Trains the XGBoost model on provided data."""
        if self.model is None:
            raise ImportError("xgboost is not installed")
        self.model.fit(X, y)
        
    def predict_risk(self, tool_call: Dict[str, Any]) -> float:
        """
        Predicts anomaly risk for a single tool call.
        
        Returns:
            float: Probability of being malicious or anomalous.
        """
        features = self.extract_structural_features(tool_call)
        
        if self.model is None or not hasattr(self.model, 'classes_'):
            # Fallback heuristic if not trained or xgboost missing
            return min(features[0] * 0.1 + features[1] * 0.5, 1.0)
            
        X = np.array([features])
        # Return probability of the positive (malicious) class
        proba = self.model.predict_proba(X)[0]
        return float(proba[1] if len(proba) > 1 else 0.0)
