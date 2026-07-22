"""
Main risk engine computing the final Sentinel Risk Index (SRI).
"""
import json
import os
from typing import Any, Dict, List, Optional
import numpy as np

from .features import FeatureExtractor
from .ml_detector import MLDetector
from .weight_learner import WeightLearner

class RiskEngine:
    """Computes the final Sentinel Risk Index (SRI) combining heuristic and ML features."""
    
    def __init__(self, weights_path: Optional[str] = None) -> None:
        self.feature_extractor = FeatureExtractor()
        self.ml_detector = MLDetector()
        self.weight_learner = WeightLearner()
        
        # Load weights if provided
        if weights_path and os.path.exists(weights_path):
            with open(weights_path, 'r') as f:
                weights_data = json.load(f)
                self.weight_learner.weights = np.array(weights_data.get('weights', self.weight_learner.weights))
                if 'intercept' in weights_data:
                    self.weight_learner.intercept = weights_data['intercept']
                
    def get_decision(self, sri_score: float) -> str:
        if sri_score <= 20:
            return "SAFE"
        elif sri_score <= 50:
            return "MONITOR"
        elif sri_score <= 80:
            return "SUSPICIOUS"
        else:
            return "BLOCKED"

    def evaluate_session(self, session_trace: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a session trace and computes the overall Sentinel Risk Index (SRI).
        
        Args:
            session_trace: The session trace containing user_prompt and tool_calls.
            
        Returns:
            Dict containing sri_score, decision, breakdown, and evidence.
        """
        # Preprocess source trust if it's string
        tool_calls = session_trace.get('tool_calls', session_trace.get('tool_sequence', []))
        processed_trace = {'user_prompt': session_trace.get('user_prompt', ''), 'tool_calls': []}
        
        for call in tool_calls:
            c = dict(call)
            trust = c.get('source_trust', 1.0)
            if isinstance(trust, str):
                c['source_trust'] = 0.1 if trust == "EXTERNAL_CONTENT" else 1.0
            if 'args' in c and 'arguments' not in c:
                c['arguments'] = c['args']
            processed_trace['tool_calls'].append(c)
            
        # Extract heuristic features
        features = self.feature_extractor.extract(processed_trace)
        cd = features.context_drift
        pv = features.policy_violation
        tr = features.transition_risk
        st = features.source_trust
        
        # Get ML feature (max risk across tools)
        ml_risk = 0.0
        for call in processed_trace['tool_calls']:
            risk = self.ml_detector.predict_risk(call)
            if risk > ml_risk:
                ml_risk = risk
                
        # Calculate SRI
        weights = self.weight_learner.get_weights()
        w1, w2, w3, w4, w5 = weights
        
        # Calculate individual weighted contributions
        cd_contrib = w1 * cd
        pv_contrib = w2 * pv
        tr_contrib = w3 * tr
        st_contrib = w4 * st
        ml_contrib = w5 * ml_risk
        
        # SRI = (w1*CD + w2*PV + w3*TR + w4*ST + w5*ML) * 100
        raw_sri = (cd_contrib + pv_contrib + tr_contrib + st_contrib + ml_contrib) * 100
        
        # Clip SRI between 0 and 100
        sri_score = max(0.0, min(100.0, float(raw_sri)))
        
        decision = self.get_decision(sri_score)
        
        return {
            "sri_score": round(sri_score, 2),
            "decision": decision,
            "breakdown": {
                "values": {
                    "CD": cd,
                    "PV": pv,
                    "TR": tr,
                    "ST": st,
                    "ML": ml_risk
                },
                "weighted_contributions": {
                    "CD": cd_contrib * 100,
                    "PV": pv_contrib * 100,
                    "TR": tr_contrib * 100,
                    "ST": st_contrib * 100,
                    "ML": ml_contrib * 100
                }
            },
            "evidence": {
                "total_calls": features.total_calls,
                "execution_depth": features.execution_depth,
                "argument_entropy": features.argument_entropy
            }
        }
