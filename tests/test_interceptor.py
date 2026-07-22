import unittest
import os
import tempfile
import json
from sentinel.interceptor import ToolTraceInterceptor

class TestInterceptor(unittest.TestCase):
    def test_interceptor_logging(self):
        interceptor = ToolTraceInterceptor()
        interceptor.start_session("test_sess_01", "Summarize PDF")
        interceptor.log_tool_call("pdf_reader", {"filepath": "resume.pdf.txt"}, "PDF Content", 1.0)
        trace = interceptor.get_trace()
        
        self.assertEqual(trace["session_id"], "test_sess_01")
        self.assertEqual(len(trace["tool_calls"]), 1)
        self.assertEqual(trace["tool_calls"][0]["tool_name"], "pdf_reader")

    def test_interceptor_export(self):
        interceptor = ToolTraceInterceptor()
        interceptor.start_session("test_sess_02", "Query DB")
        interceptor.log_tool_call("database_tool", {"action": "SELECT"}, "DB Rows", 1.0)
        
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name
            
        interceptor.export_trace_json(tmp_path)
        self.assertTrue(os.path.exists(tmp_path))
        
        with open(tmp_path, "r") as f:
            data = json.load(f)
        self.assertEqual(data["session_id"], "test_sess_02")
        self.assertEqual(len(data["tool_calls"]), 1)
        os.remove(tmp_path)

    def test_interceptor_log_without_start_raises(self):
        interceptor = ToolTraceInterceptor()
        with self.assertRaises(RuntimeError):
            interceptor.log_tool_call("tool", {}, "out")

if __name__ == "__main__":
    unittest.main()
