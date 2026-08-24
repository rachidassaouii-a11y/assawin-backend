from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.all_models import Projet, Devis, User

router = APIRouter(prefix="/api/v1/projets", tags=["Projets & Cockpit"])

# ===== SCHÉMAS PYDANTIC =====

class ProjetCreate(BaseModel):
    nom_projet: str = Field(..., min_length=1)
    budget_initial_ht: float = Field(0.0, ge=0)
    marge_cible_pct: float = Field(30.0, ge=0, le=100)
    statut: str = Field("EN_COURS")
    description: Optional[str] = None

class ProjetResponse(BaseModel):
    id_projet: str
    nom_projet: str
    budget_initial_ht: float
    marge_cible_pct: float
    statut: str
    description: Optional[str]
    
    class Config:
        from_attributes = True


# ===== ENDPOINTS PROJETS & COCKPIT =====

@router.post("/", status_code=201, response_model=ProjetResponse)
def create_projet(
    data: ProjetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crée un nouveau projet lié à l'utilisateur connecté via son id_user.
    """
    nouveau_projet = Projet(
        id_projet=uuid.uuid4(),
        id_user=current_user.id_user,
        nom_projet=data.nom_projet,
        budget_initial_ht=data.budget_initial_ht,
        marge_cible_pct=data.marge_cible_pct,
        statut=data.statut,
        description=data.description,
        date_creation=datetime.now(timezone.utc)
    )
    db.add(nouveau_projet)
    db.commit()
    db.refresh(nouveau_projet)
    return nouveau_projet


@router.get("/", response_model=List[ProjetResponse])
def list_projets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Liste tous les projets de l'utilisateur connecté.
    """
    projets = db.query(Projet).filter(Projet.id_user == current_user.id_user).all()
    return projets


@router.get("/{projet_id}/cockpit")
def get_projet_cockpit(
    projet_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère la synthèse financière et le Truth Gate d'un projet via ses devis rattachés.
    """
    try:
        proj_uuid = uuid.UUID(projet_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Format UUID projet invalide")

    projet = db.query(Projet).filter(
        Projet.id_projet == proj_uuid,
        Projet.id_user == current_user.id_user
    ).first()

    if not projet:
        raise HTTPException(status_code=404, detail="Projet introuvable ou non autorisé")

    # Récupération des devis associés pour le calcul du cockpit
    devis_list = db.query(Devis).filter(Devis.id_projet == projet.id_projet).all()
    
    total_devis_ht = sum(d.total_ht for d in devis_list)
    total_cout = sum(d.cout_total for d in devis_list)
    marge_globale_eur = total_devis_ht - total_cout
    taux_marque_global = round((marge_globale_eur / total_devis_ht) * 100, 2) if total_devis_ht > 0 else 0.0

    return {
        "id_projet": str(projet.id_projet),
        "nom_projet": projet.nom_projet,
        "statut": projet.statut,
        "budget_initial_ht": projet.budget_initial_ht,
        "marge_cible_pct": projet.marge_cible_pct,
        "total_devis_ht": total_devis_ht,
        "total_cout": total_cout,
        "marge_globale_eur": marge_globale_eur,
        "taux_marque_global": taux_marque_global,
        "can_send": taux_marque_global >= 20.0,
        "nombre_devis": len(devis_list)
    }
    
    
