import unittest
from sentinel.features import (
    compute_context_drift,
    compute_policy_violation,
    compute_transition_risk,
    compute_source_trust,
    FeatureExtractor
)

class TestFeatures(unittest.TestCase):
    def test_compute_context_drift(self):
        prompt = "read file"
        tools = [{"tool_name": "read_file", "args": {"file": "file"}}]
        drift = compute_context_drift(prompt, tools)
        self.assertTrue(0.0 <= drift <= 1.0)

    def test_compute_policy_violation(self):
        tools = [
            {"tool_name": "database_tool", "args": {"action": "DELETE"}, "source_trust": 0.1}
        ]
        pv = compute_policy_violation(tools)
        self.assertTrue(pv >= 0.0)

    def test_compute_transition_risk(self):
        tools = [
            {"tool_name": "pdf_reader", "args": {"path": "script.sh"}, "source_trust": 1.0},
            {"tool_name": "database_tool", "args": {"cmd": "DELETE"}, "source_trust": 1.0}
        ]
        tr = compute_transition_risk(tools)
        self.assertTrue(0.0 <= tr <= 1.0)

    def test_compute_source_trust(self):
        tools = [
            {"tool_name": "tool1", "source_trust": 0.8},
            {"tool_name": "tool2", "source_trust": 0.2},
        ]
        st = compute_source_trust(tools)
        self.assertEqual(st, 0.2)

    def test_feature_extractor(self):
        extractor = FeatureExtractor()
        trace = {
            "user_prompt": "read file",
            "tool_calls": [{"tool_name": "pdf_reader", "args": {}, "source_trust": 1.0}]
        }
        fv = extractor.extract(trace)
        self.assertIsNotNone(fv)

if __name__ == "__main__":
    unittest.main()
    session_trace = {
        "user_prompt": "do something",
        "tool_calls": [
            {"tool_name": "read_file", "args": {"path": "foo.txt"}, "source_trust": 0.5},
            {"tool_name": "run_command", "args": {"cmd": "echo hello"}, "source_trust": 0.9}
        ]
    }
    
    features = extractor.extract(session_trace)
    assert features.total_calls == 2
    assert features.execution_depth == 2
    
    vec = features.to_array()
    assert len(vec) == 7
    
    d = features.to_dict()
    assert "context_drift" in d
    assert "policy_violation" in d
