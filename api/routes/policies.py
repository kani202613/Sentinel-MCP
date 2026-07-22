from fastapi import APIRouter, Depends
from typing import List
from ..models import Policy
from ..auth import verify_token

router = APIRouter(prefix="/policies", tags=["policies"])

@router.get("", response_model=List[Policy])
def get_policies(username: str = Depends(verify_token)):
    return [
        Policy(
            policy_id="pol-001",
            name="Block High SRI",
            description="Block any session with an SRI score > 80.",
            active=True
        )
    ]
