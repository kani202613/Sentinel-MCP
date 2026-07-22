"""
Feature extractor for Sentinel Risk Index (SRI) components.
"""
from typing import Any, Dict, List

def compute_context_drift(user_prompt: str, tool_call: Dict[str, Any]) -> float:
    """
    Computes the semantic drift between the initial user prompt and the tool call.
    
    Args:
        user_prompt (str): The original user instruction.
        tool_call (Dict[str, Any]): The tool call dictionary.
        
    Returns:
        float: A value between 0.0 and 1.0 representing context drift.
    """
    # Stub for MiniLM embedding comparison
    # In practice, we would embed both and calculate cosine distance
    return 0.1

def compute_policy_violation(tool_call: Dict[str, Any], policy_rules: List[Dict[str, Any]]) -> float:
    """
    Computes the extent of policy violation for a given tool call.
    
    Args:
        tool_call (Dict[str, Any]): The tool call to analyze.
        policy_rules (List[Dict[str, Any]]): Security policy rules.
        
    Returns:
        float: A risk score indicating policy violation (0.0 to 1.0).
    """
    return 0.0

def compute_transition_risk(prev_tool: str, curr_tool: str) -> float:
    """
    Computes the risk associated with transitioning from one tool to another.
    
    Args:
        prev_tool (str): The previously called tool.
        curr_tool (str): The current tool being called.
        
    Returns:
        float: Transition risk score.
    """
    # Example simple logic for high-risk transitions
    dangerous_transitions = {
        ("read_file", "run_command"): 0.8,
        ("search_web", "write_to_file"): 0.6,
    }
    return dangerous_transitions.get((prev_tool, curr_tool), 0.1)

def compute_source_trust(instruction_source: str) -> float:
    """
    Computes a trust score based on the source of the instruction.
    
    Args:
        instruction_source (str): Source of the instruction (e.g., 'user', 'system', 'agent').
        
    Returns:
        float: Trust risk score (higher score means lower trust/higher risk).
    """
    trust_map = {
        "user": 0.1,
        "system": 0.0,
        "agent": 0.5,
        "external_web": 0.9
    }
    return trust_map.get(instruction_source, 0.5)
