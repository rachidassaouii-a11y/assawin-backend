from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import List
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.all_models import Devis, User

router = APIRouter(prefix="/api/v1/truthgate", tags=["Truth Gate"])

class TruthGateCheckRequest(BaseModel):
    id_devis: str

class TruthGateIssue(BaseModel):
    code: str
    severity: str  # "BLOCKING" ou "WARNING"
    message: str

class TruthGateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    score: int
    can_send: bool
    blocking_count: int
    warning_count: int
    issues: List[TruthGateIssue]

@router.post("/validate", response_model=TruthGateResponse)
def validate_devis(
    payload: TruthGateCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        uid = uuid.UUID(payload.id_devis)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID devis invalide")

    devis = db.query(Devis).filter(
        Devis.id_devis == uid,
        Devis.id_user == current_user.id_user
    ).first()

    if not devis:
        raise HTTPException(status_code=404, detail="Devis introuvable")

    issues: List[TruthGateIssue] = []
    score = 100

    # RÈGLE 1 : Marge cible minimale
    marge = float(devis.marge_cible_pct or 0)
    if marge < 20.0:
        score -= 40
        issues.append(TruthGateIssue(
            code="LOW_MARGIN_CRITICAL",
            severity="BLOCKING",
            message=f"Marge insuffisante ({marge}%). Seuil critique fixé à 20%."
        ))
    elif marge < 30.0:
        score -= 15
        issues.append(TruthGateIssue(
            code="LOW_MARGIN_WARNING",
            severity="WARNING",
            message=f"Marge à {marge}%. Recommandation : viser au moins 30%."
        ))

    # RÈGLE 2 : Montant Total HT
    montant_ht = float(devis.montant_total_ht or 0)
    if montant_ht <= 0:
        score -= 50
        issues.append(TruthGateIssue(
            code="ZERO_TOTAL",
            severity="BLOCKING",
            message="Le montant total HT du devis ne peut pas être nul."
        ))

    blocking_count = sum(1 for i in issues if i.severity == "BLOCKING")
    warning_count = sum(1 for i in issues if i.severity == "WARNING")
    can_send = blocking_count == 0

    return TruthGateResponse(
        score=max(score, 0),
        can_send=can_send,
        blocking_count=blocking_count,
        warning_count=warning_count,
        issues=issues
    )
