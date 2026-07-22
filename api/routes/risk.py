from fastapi import APIRouter, Depends
from ..models import RiskStats
from ..auth import verify_token

router = APIRouter(prefix="/risk", tags=["risk"])

@router.get("", response_model=RiskStats)
def get_risk(username: str = Depends(verify_token)):
    return RiskStats(
        average_sri=45.2,
        critical_alerts=12,
        active_sessions=150
    )
