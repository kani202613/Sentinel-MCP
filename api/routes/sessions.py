from fastapi import APIRouter, Depends
from typing import List
from datetime import datetime
from ..models import SessionSummary
from ..auth import verify_token

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.get("", response_model=List[SessionSummary])
def get_sessions(username: str = Depends(verify_token)):
    return [
        SessionSummary(
            session_id="sess-001",
            timestamp=datetime.utcnow(),
            sri_score=85.5,
            status="Suspicious"
        ),
        SessionSummary(
            session_id="sess-002",
            timestamp=datetime.utcnow(),
            sri_score=15.2,
            status="Safe"
        )
    ]
