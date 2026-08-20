from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.all_models import Devis, User

router = APIRouter(prefix="/api/v1/devis", tags=["Devis & Transaction"])

class DevisStatusUpdate(BaseModel):
    statut: str  # "BROUILLON", "ENVOYE", "SIGNE", "REFUSE"

@router.get("/{id_devis}/pdf-preview")
def get_pdf_preview(
    id_devis: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        uid = uuid.UUID(id_devis)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID devis invalide")

    devis = db.query(Devis).filter(
        Devis.id_devis == uid,
        Devis.id_user == current_user.id_user
    ).first()

    if not devis:
        raise HTTPException(status_code=404, detail="Devis introuvable")

    return {
        "reference": devis.reference or f"DEV-{id_devis[:8]}",
        "montant_ht": float(devis.montant_total_ht or 0),
        "tva_pct": float(devis.tva_pct or 20.0),
        "montant_ttc": float(devis.montant_total_ht or 0) * (1 + float(devis.tva_pct or 20.0) / 100),
        "status": devis.statut or "BROUILLON"
    }

@router.post("/{id_devis}/send")
def send_devis_to_client(
    id_devis: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        uid = uuid.UUID(id_devis)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID devis invalide")

    devis = db.query(Devis).filter(
        Devis.id_devis == uid,
        Devis.id_user == current_user.id_user
    ).first()

    if not devis:
        raise HTTPException(status_code=404, detail="Devis introuvable")

    devis.statut = "ENVOYE"
    db.commit()

    return {"status": "success", "message": "Devis envoyé au client avec succès"}
