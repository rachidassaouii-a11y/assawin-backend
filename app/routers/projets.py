import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.all_models import Projet, Devis, Client


router = APIRouter(tags=["Projets"])


# =====================================================
# SCHEMAS
# =====================================================

class ProjetCreate(BaseModel):
    nom: str
    budget_initial_ht: float = 0.0
    client_id: Optional[str] = None


class ProjectInfo(BaseModel):
    id: str
    nom: str
    client_id: Optional[str] = None


# =====================================================
# CREATION PROJET
# =====================================================

@router.post(
    "",
    response_model=ProjectInfo,
    status_code=status.HTTP_201_CREATED
)
async def create_projet(
    payload: ProjetCreate,
    db: Session = Depends(get_db)
):

    if payload.client_id:

        client = (
            db.query(Client)
            .filter(Client.id == payload.client_id)
            .first()
        )

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client introuvable"
            )

    nouveau_projet = Projet(
        id=str(uuid.uuid4()),
        nom_projet=payload.nom,
        budget_initial_ht=payload.budget_initial_ht,
        client_id=payload.client_id
    )

    db.add(nouveau_projet)
    db.commit()
    db.refresh(nouveau_projet)

    return ProjectInfo(
        id=str(nouveau_projet.id),
        nom=nouveau_projet.nom_projet,
        client_id=nouveau_projet.client_id
    )


# =====================================================
# COCKPIT PROJET
# =====================================================

@router.get("/{project_id}/cockpit")
async def get_project_cockpit(
    project_id: uuid.UUID,
    db: Session = Depends(get_db)
):

    str_project_id = str(project_id)

    projet = (
        db.query(Projet)
        .filter(Projet.id == str_project_id)
        .first()
    )

    if not projet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projet non trouvé"
        )

    devis_list = (
        db.query(Devis)
        .filter(Devis.projet_id == projet.id)
        .all()
    )

    budget = float(
        projet.budget_initial_ht or 0.0
    )

    debourse = sum(
        float(
            getattr(d, "cout_total", 0.0) or 0.0
        )
        for d in devis_list
    )

    vente = sum(
        float(
            getattr(d, "total_ht", 0.0) or 0.0
        )
        for d in devis_list
    )

    marge = vente - debourse

    marge_pct = (
        marge / vente * 100
        if vente > 0
        else 0.0
    )

    client_data = None

    if projet.client:
        client_data = {
            "id": projet.client.id,
            "nom": projet.client.nom,
            "type_client": projet.client.type_client
        }

    return {

        "project": {
            "id": str(projet.id),
            "name": projet.nom_projet,
            "nom": projet.nom_projet,
            "client": client_data
        },

        "financials": {
            "budget": budget,
            "debourse": debourse,
            "vente": vente,
            "marge": marge,
            "marge_pct": round(
                marge_pct,
                2
            )
        },

        "risk": {
            "exposition": 0.0
        },

        "progress": {
            "pourcentage": 0.0
        },

        "alerts": [],

        "decisions": [],

        "updated_at": datetime.now(
            timezone.utc
        ).isoformat()
    }
