from fastapi import APIRouter, Depends
from typing import List
from datetime import datetime
from ..models import Alert
from ..auth import verify_token

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("", response_model=List[Alert])
def get_alerts(username: str = Depends(verify_token)):
    return [
        Alert(
            alert_id="alt-001",
            session_id="sess-001",
            severity="Critical",
            message="Suspicious process injection detected.",
            timestamp=datetime.utcnow()
        )
    ]
