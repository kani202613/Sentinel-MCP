from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from sentinel.risk_engine import RiskEngine

app = FastAPI(title="SentinelMCP API")
risk_engine = RiskEngine()

class TracePayload(BaseModel):
    user_prompt: str
    tool_calls: List[Dict[str, Any]]

@app.post("/api/v1/analyze")
def analyze_trace(payload: TracePayload):
    try:
        session_trace = payload.model_dump()
    except AttributeError:
        session_trace = payload.dict()
    try:
        result = risk_engine.evaluate_session(session_trace)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
