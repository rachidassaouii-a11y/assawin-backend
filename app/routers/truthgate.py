from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/v1/truthgate", tags=["Truth Gate"])

class TruthGateCheckRequest(BaseModel):
    id_devis: str

class TruthGateIssue(BaseModel):
    code: str
    severity: str
    message: str

class TruthGateResponse(BaseModel):
    score: int
    can_send: bool
    blocking_count: int
    warning_count: int
    issues: List[TruthGateIssue]

@router.post("/validate", response_model=TruthGateResponse)
def validate_devis(payload: TruthGateCheckRequest):
    return TruthGateResponse(
        score=85,
        can_send=True,
        blocking_count=0,
        warning_count=1,
        issues=[
            TruthGateIssue(
                code="LOW_MARGIN_WARNING",
                severity="WARNING",
                message="Marge à 25%. Recommandation : viser au moins 30%."
            )
        ]
    )
