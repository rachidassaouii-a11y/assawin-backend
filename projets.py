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
            "id": str(projet.id),
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
            "exposition": 0.0  # À brancher sur ton Risk Engine
        },
        "progress": {
            "pourcentage": 0.0
        },
        "alerts": [],
        "decisions": [],
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
