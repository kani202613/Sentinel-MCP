import unittest
from sentinel.risk_engine import RiskEngine

class TestRiskEngine(unittest.TestCase):
    def test_risk_engine_decisions(self):
        engine = RiskEngine()
        
        self.assertEqual(engine.get_decision(10), "SAFE")
        self.assertEqual(engine.get_decision(20), "SAFE")
        self.assertEqual(engine.get_decision(30), "MONITOR")
        self.assertEqual(engine.get_decision(50), "MONITOR")
        self.assertEqual(engine.get_decision(60), "SUSPICIOUS")
        self.assertEqual(engine.get_decision(80), "SUSPICIOUS")
        self.assertEqual(engine.get_decision(90), "BLOCKED")
        self.assertEqual(engine.get_decision(100), "BLOCKED")

    def test_risk_engine_evaluate_session(self):
        engine = RiskEngine()
        
        session_trace = {
            "user_prompt": "Help me read a file and run a command.",
            "tool_calls": [
                {"tool_name": "pdf_reader", "args": {"path": "resume.pdf.txt"}, "source_trust": 0.1},
                {"tool_name": "database_tool", "args": {"cmd": "DELETE"}, "source_trust": 0.1}
            ]
        }
        
        result = engine.evaluate_session(session_trace)
        
        self.assertIn("sri_score", result)
        self.assertIn("decision", result)
        self.assertIn("breakdown", result)
        
        sri_score = result["sri_score"]
        self.assertTrue(0.0 <= sri_score <= 100.0)

if __name__ == "__main__":
    unittest.main()
    assert "ST" in breakdown
    assert "ML" in breakdown
