from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class RiskComponents(BaseModel):
    CD: float
    PV: float
    TR: float
    ST: float
    ML: float

class AnalysisRequest(BaseModel):
    session_id: str
    trace_data: Dict[str, Any]

class AnalysisResponse(BaseModel):
    session_id: str
    decision: str
    sri_score: float
    components: RiskComponents

class SessionSummary(BaseModel):
    session_id: str
    timestamp: datetime
    sri_score: float
    status: str

class Alert(BaseModel):
    alert_id: str
    session_id: str
    severity: str
    message: str
    timestamp: datetime

class Policy(BaseModel):
    policy_id: str
    name: str
    description: str
    active: bool

class RiskStats(BaseModel):
    average_sri: float
    critical_alerts: int
    active_sessions: int
