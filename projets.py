import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

# Imports de ta structure existante (à ajuster selon tes chemins réels)
from app.core.database import get_db
from app.core.security import get_current_user  # Ajuste le chemin si nécessaire
from app.models.all_models import Projet, Devis, User

router = APIRouter(prefix="/api/v1/projets", tags=["Cockpit"])

# --- Routeur principal (Protégé par JWT et typé UUID) ---
@router.get("/{project_id}/cockpit")
async def get_project_cockpit(
    project_id: uuid.UUID,  # Validation automatique du format UUID (évite la 500)
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Renvoie 401 si non connecté
):
    """
    Lecture des données via l'ORM.
    Vérifie que le projet appartient bien à l'utilisateur connecté.
    """

    # 1. Récupération du projet en s'assurant qu'il appartient à l'utilisateur
    projet = db.query(Projet).filter(
        Projet.id == project_id,
        Projet.user_id == current_user.id  # Vérification d'appartenance
    ).first()
    
    if not projet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projet non trouvé"
        )

    # 2. Agrégation des données financières via l'ORM
    devis = db.query(Devis).filter(Devis.projet_id == projet.id).all()
    
    budget = sum(d.budget_initial_ht for d in devis) if devis else projet.budget_initial_ht or 0.0
    debourse = sum(d.cout_total for d in devis) if devis else 0.0
    vente = sum(d.total_ht for d in devis) if devis else 0.0
    marge = vente - debourse
    marge_pct = (marge / vente * 100) if vente > 0 else 0.0

    return {
        "project": {
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.all_models import Projet, Devis, User

router = APIRouter(prefix="/api/v1/projets", tags=["Projets"])

# --- Schémas Pydantic ---
class ProjetCreate(BaseModel):
    nom: str
    budget_initial_ht: float = 0.0

class ProjectInfo(BaseModel):
    id: str
    nom: str

# --- Route POST : Création de projet sécurisée ---
@router.post("", response_model=ProjectInfo, status_code=status.HTTP_201_CREATED)
async def create_projet(
    payload: ProjetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crée un nouveau projet pour l'utilisateur connecté et retourne son UUID.
    """
    nouveau_projet = Projet(
        id=uuid.uuid4(),
        nom_projet=payload.nom,
        budget_initial_ht=payload.budget_initial_ht,
        user_id=current_user.id
    )
    db.add(nouveau_projet)
    db.commit()
    db.refresh(nouveau_projet)

    return ProjectInfo(id=str(nouveau_projet.id), nom=nouveau_projet.nom_projet)

# --- Route GET : Cockpit Projet (Protégé JWT + Typage UUID) ---
@router.get("/{project_id}/cockpit")
async def get_project_cockpit(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Extrait les agrégats financiers du projet pour l'utilisateur connecté.
    """
    projet = db.query(Projet).filter(
        Projet.id == project_id,
        Projet.user_id == current_user.id
    ).first()
    
    if not projet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projet non trouvé"
        )

    devis_list = db.query(Devis).filter(Devis.projet_id == projet.id).all()
    
    # Correction : budget est issu de projet, les totaux/déboursés viennent des devis
    budget = float(projet.budget_initial_ht or 0.0)
    debourse = sum(float(getattr(d, 'cout_total', 0.0) or 0.0) for d in devis_list) if devis_list else 0.0
    vente = sum(float(getattr(d, 'total_ht', 0.0) or 0.0) for d in devis_list) if devis_list else 0.0
    
    marge = vente - debourse
    marge_pct = (marge / vente * 100) if vente > 0 else 0.0

    return {
        "project": {
            "id": str(projet.id),
            "name": projet.nom_projet,
            "nom": projet.nom_projet
        },
        "financials": {
            "budget": budget,
            "debourse": debourse,
            "vente": vente,
            "marge": marge,
            "marge_pct": round(marge_pct, 2)
        },
        "risk": {
            "exposition": 0.0
        },
        "progress": {
            "pourcentage": 0.0
        },
        "alerts": [],
        "decisions": [],
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
