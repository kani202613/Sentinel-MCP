import json
import time
from typing import Any, Dict, List, Optional

class ToolTraceInterceptor:
    """Captures and logs tool execution sessions."""
    
    def __init__(self):
        self.session_id: Optional[str] = None
        self.user_prompt: Optional[str] = None
        self.tool_calls: List[Dict[str, Any]] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.active: bool = False

    def start_session(self, session_id: str, user_prompt: str) -> None:
        """Starts a new tracing session."""
        self.session_id = session_id
        self.user_prompt = user_prompt
        self.tool_calls = []
        self.start_time = time.time()
        self.end_time = None
        self.active = True

    def log_tool_call(self, tool_name: str, args: Dict[str, Any], output: Any, source_trust: float = 1.0) -> None:
        """Logs a tool call with its arguments, output, and trust score."""
        if not self.active:
            raise RuntimeError("Session not active. Call start_session first.")
        
        self.tool_calls.append({
            "tool_name": tool_name,
            "args": args,
            "output": output,
            "source_trust": source_trust,
            "timestamp": time.time()
        })

    def end_session(self) -> None:
        """Ends the current tracing session."""
        self.end_time = time.time()
        self.active = False

    def get_trace(self) -> Dict[str, Any]:
        """Returns the full trace of the current or last session."""
        return {
            "session_id": self.session_id,
            "user_prompt": self.user_prompt,
            "tool_calls": self.tool_calls,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": (self.end_time or time.time()) - (self.start_time or time.time())
        }

    def export_trace_json(self, filepath: str) -> None:
        """Exports the trace to a JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.get_trace(), f, indent=2, ensure_ascii=False)
