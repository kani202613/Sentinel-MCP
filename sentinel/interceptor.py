"""
Interceptor module for capturing complete tool traces.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time

@dataclass
class ToolCallRecord:
    """Represents a single tool call capture."""
    tool_name: str
    arguments: Dict[str, Any]
    output: Any = None
    timestamp: float = field(default_factory=time.time)
    instruction_source: str = "user"  # "user", "agent", "system"

@dataclass
class TraceRecord:
    """Represents a complete tool trace."""
    user_prompt: str
    tool_calls: List[ToolCallRecord] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    
class ToolTraceInterceptor:
    """Captures complete tool traces (User prompt, Tool calls, Arguments, Outputs)."""
    
    def __init__(self) -> None:
        self.traces: List[TraceRecord] = []
        self.current_trace: Optional[TraceRecord] = None
        
    def start_trace(self, user_prompt: str) -> None:
        """Starts capturing a new trace based on a user prompt."""
        self.current_trace = TraceRecord(user_prompt=user_prompt)
        
    def add_tool_call(self, tool_name: str, arguments: Dict[str, Any], instruction_source: str = "user") -> ToolCallRecord:
        """Records a tool call within the current trace."""
        if self.current_trace is None:
            raise RuntimeError("No active trace. Call start_trace() first.")
        record = ToolCallRecord(tool_name=tool_name, arguments=arguments, instruction_source=instruction_source)
        self.current_trace.tool_calls.append(record)
        return record
        
    def record_tool_output(self, record: ToolCallRecord, output: Any) -> None:
        """Records the output for a previously captured tool call."""
        record.output = output
        
    def end_trace(self) -> TraceRecord:
        """Finalizes and stores the current trace."""
        if self.current_trace is None:
            raise RuntimeError("No active trace to end.")
        trace = self.current_trace
        self.traces.append(trace)
        self.current_trace = None
        return trace
