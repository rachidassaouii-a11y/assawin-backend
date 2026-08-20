from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.all_models import Devis, Projet, User

router = APIRouter(prefix="/api/v1/projets", tags=["Chantiers & Projets"])

@router.post("/convert/{id_devis}")
def convert_devis_to_projet(
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

    # Instanciation du nouveau chantier
    nouveau_projet = Projet(
        id_projet=uuid.uuid4(),
        id_user=current_user.id_user,
        nom_projet=f"Chantier - {devis.reference or id_devis[:8]}",
        budget_prevu=devis.montant_total_ht,
        statut="EN_COURS"
    )

    devis.statut = "SIGNE"
    
    db.add(nouveau_projet)
    db.commit()

    return {
        "status": "success",
        "message": "Chantier créé avec succès",
        "id_projet": str(nouveau_projet.id_projet)
    }
