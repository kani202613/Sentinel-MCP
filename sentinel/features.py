import math
import re
from typing import Any, Dict, List
from collections import Counter

# Optional dependency for better semantic drift, fallback to TF-IDF
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def _compute_cosine_similarity_fallback(text1: str, text2: str) -> float:
    """Fallback cosine similarity using basic term frequency."""
    def get_words(text: str) -> List[str]:
        return re.findall(r'\w+', text.lower())
    
    vec1 = Counter(get_words(text1))
    vec2 = Counter(get_words(text2))
    
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])
    
    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    
    if not denominator:
        return 0.0
    return float(numerator) / denominator


def compute_context_drift(user_prompt: str, tool_sequence: List[Dict[str, Any]]) -> float:
    """Computes semantic drift between user prompt and tool arguments."""
    if not tool_sequence or not user_prompt:
        return 0.0

    tool_text = " ".join([
        f"{call.get('tool_name', '')} " + " ".join(str(v) for v in call.get('args', {}).values())
        for call in tool_sequence
    ])

    if SKLEARN_AVAILABLE:
        try:
            vectorizer = TfidfVectorizer().fit_transform([user_prompt, tool_text])
            vectors = vectorizer.toarray()
            sim = cosine_similarity([vectors[0]], [vectors[1]])[0][0]
        except Exception:
            sim = _compute_cosine_similarity_fallback(user_prompt, tool_text)
    else:
        sim = _compute_cosine_similarity_fallback(user_prompt, tool_text)
        
    # Drift is inverse of similarity, range [0, 1]
    # 0.0 means perfect alignment, 1.0 means total drift
    return max(0.0, min(1.0, 1.0 - sim))


def compute_policy_violation(tool_sequence: List[Dict[str, Any]]) -> float:
    """Evaluates policy rules, returning [0.0, 1.0]."""
    violation_score = 0.0
    
    dangerous_tools = {'delete_db', 'drop_table', 'execute_sql', 'eval', 'exec', 'system_shell', 'run_command'}
    sensitive_args = {'password', 'secret', 'token', 'key', 'credential', '.env', 'id_rsa'}
    
    for call in tool_sequence:
        tool_name = call.get('tool_name', '').lower()
        args = call.get('args', {})
        source_trust = call.get('source_trust', 1.0)
        
        # Policy: dangerous tools from untrusted sources
        if tool_name in dangerous_tools and source_trust < 0.5:
            violation_score += 0.8
            
        # Policy: dangerous tools in general
        elif tool_name in dangerous_tools:
            violation_score += 0.4
            
        # Policy: accessing sensitive files/args
        for arg_val in args.values():
            val_str = str(arg_val).lower()
            if any(sensitive in val_str for sensitive in sensitive_args):
                # if untrusted source reading secrets
                if source_trust < 0.5:
                    violation_score += 0.9
                else:
                    violation_score += 0.3
                    
    return max(0.0, min(1.0, violation_score))


def compute_transition_risk(tool_sequence: List[Dict[str, Any]]) -> float:
    """Computes anomaly score for transitions between tools."""
    if len(tool_sequence) < 2:
        return 0.0
        
    risk_score = 0.0
    
    # Define some risky transitions (e.g., reading untrusted file -> executing shell/db command)
    risky_transitions = [
        ({'read_file', 'fetch_url', 'download', 'pdf_reader'}, {'run_command', 'execute_sql', 'system_shell', 'eval'}),
        ({'get_secret', 'read_env'}, {'send_http', 'upload_file', 'fetch_url'}) # exfiltration
    ]
    
    for i in range(len(tool_sequence) - 1):
        prev_tool = tool_sequence[i].get('tool_name', '').lower()
        next_tool = tool_sequence[i+1].get('tool_name', '').lower()
        
        for source_set, target_set in risky_transitions:
            if prev_tool in source_set and next_tool in target_set:
                risk_score += 0.5
                
    return max(0.0, min(1.0, risk_score))


def compute_source_trust(tool_sequence: List[Dict[str, Any]]) -> float:
    """Evaluates trust score of instruction sources."""
    if not tool_sequence:
        return 1.0
        
    trust_scores = [call.get('source_trust', 1.0) for call in tool_sequence]
    
    # Take the minimum trust score in the chain (taint analysis).
    return min(trust_scores)


def _compute_argument_entropy(tool_sequence: List[Dict[str, Any]]) -> float:
    """Computes basic entropy/complexity of arguments."""
    if not tool_sequence:
        return 0.0
        
    all_args = str([call.get('args', {}) for call in tool_sequence])
    if not all_args:
        return 0.0
        
    char_counts = Counter(all_args)
    entropy = 0.0
    total_chars = len(all_args)
    
    for count in char_counts.values():
        p = count / total_chars
        if p > 0:
            entropy -= p * math.log2(p)
            
    # Normalize somewhat for feature scaling (typical ascii entropy is ~4-5)
    return min(1.0, entropy / 8.0)


class FeatureVector:
    def __init__(self, 
                 context_drift: float, 
                 policy_violation: float,
                 transition_risk: float,
                 source_trust: float,
                 execution_depth: int,
                 argument_entropy: float,
                 total_calls: int):
        self.context_drift = context_drift
        self.policy_violation = policy_violation
        self.transition_risk = transition_risk
        self.source_trust = source_trust
        self.execution_depth = execution_depth
        self.argument_entropy = argument_entropy
        self.total_calls = total_calls

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context_drift": self.context_drift,
            "policy_violation": self.policy_violation,
            "transition_risk": self.transition_risk,
            "source_trust": self.source_trust,
            "execution_depth": self.execution_depth,
            "argument_entropy": self.argument_entropy,
            "total_calls": self.total_calls
        }
        
    def to_array(self) -> List[float]:
        return [
            self.context_drift,
            self.policy_violation,
            self.transition_risk,
            self.source_trust,
            float(self.execution_depth),
            self.argument_entropy,
            float(self.total_calls)
        ]


class FeatureExtractor:
    """Extracts features from a raw session trace."""
    
    def extract(self, session_trace: Dict[str, Any]) -> FeatureVector:
        user_prompt = session_trace.get('user_prompt', '')
        tool_sequence = session_trace.get('tool_calls', [])
        
        context_drift = compute_context_drift(user_prompt, tool_sequence)
        policy_violation = compute_policy_violation(tool_sequence)
        transition_risk = compute_transition_risk(tool_sequence)
        source_trust = compute_source_trust(tool_sequence)
        
        execution_depth = len(tool_sequence)
        argument_entropy = _compute_argument_entropy(tool_sequence)
        total_calls = len(tool_sequence)
        
        return FeatureVector(
            context_drift=context_drift,
            policy_violation=policy_violation,
            transition_risk=transition_risk,
            source_trust=source_trust,
            execution_depth=execution_depth,
            argument_entropy=argument_entropy,
            total_calls=total_calls
        )
