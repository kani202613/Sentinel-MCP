"""
Main risk engine computing the final Sentinel Risk Index (SRI).
"""
from typing import Any, Dict, List, Optional
import numpy as np

from .features import (
    compute_context_drift,
    compute_policy_violation,
    compute_transition_risk,
    compute_source_trust
)
from .ml_detector import MLDetector
from .weight_learner import WeightLearner

class RiskEngine:
    """Computes the final Sentinel Risk Index (SRI) combining heuristic and ML features."""
    
    def __init__(self, policy_rules: Optional[List[Dict[str, Any]]] = None) -> None:
        self.policy_rules = policy_rules or []
        self.ml_detector = MLDetector()
        self.weight_learner = WeightLearner()
        self.previous_tool_name = "START"
        
    def evaluate_tool_call(self, user_prompt: str, tool_call: Dict[str, Any], instruction_source: str = "user") -> float:
        """
        Evaluates a tool call and computes the overall Sentinel Risk Index (SRI).
        
        Args:
            user_prompt: The main conversation or task prompt.
            tool_call: The tool call payload (should include 'name' and 'arguments').
            instruction_source: The origin of the instruction triggering this tool.
            
        Returns:
            float: The computed SRI (0.0 to 1.0).
        """
        tool_name = tool_call.get("name", "unknown")
        
        # 1. Semantic Context Drift
        f1 = compute_context_drift(user_prompt, tool_call)
        
        # 2. Policy Violation Risk
        f2 = compute_policy_violation(tool_call, self.policy_rules)
        
        # 3. Transition Risk
        f3 = compute_transition_risk(self.previous_tool_name, tool_name)
        
        # 4. Source Trust Risk
        f4 = compute_source_trust(instruction_source)
        
        # 5. ML-based Structural Risk
        f5 = self.ml_detector.predict_risk(tool_call)
        
        # Combine features
        features = np.array([f1, f2, f3, f4, f5])
        
        # Calculate final SRI
        sri_score = self.weight_learner.predict_combined_risk(features)
        
        # Update state for next evaluation
        self.previous_tool_name = tool_name
        
        return sri_score
