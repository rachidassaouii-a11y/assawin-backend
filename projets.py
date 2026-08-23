from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from uuid import UUID

# Imports de ta structure existante
from app.core.database import get_db
# Imports des modèles (AJOUTER User)
from app.models.all_models import Projet, Devis, Alerte, Decision, Avancement, User
# Import de ta dépendance d'authentification (adapter si besoin)
from app.core.auth import get_current_user

router = APIRouter(prefix="/api/v1/projets", tags=["Cockpit"])

# --- Schémas Pydantic (Contrat strict inchangé) ---
class ProjectInfo(BaseModel):
    id: str
    nom: str

class Financials(BaseModel):
    budget: float
    debourse: float
    vente: float
    marge: float
    marge_pct: float

class RiskInfo(BaseModel):
    exposition: float

class ProgressInfo(BaseModel):
    pourcentage: float

class AlertInfo(BaseModel):
    id: str
    niveau: str
    message: str

class DecisionInfo(BaseModel):
    id: str
    date: str
    action: str

class CockpitResponse(BaseModel):
    projet: ProjectInfo
    financials: Financials
    risque: RiskInfo
    avancement: ProgressInfo
    alertes: List[AlertInfo]
    decisions: List[DecisionInfo]
    updated_at: str


# --- Routeur principal (Sécurisé et connecté aux vrais modèles) ---
@router.get("/{projet_id}/cockpit", response_model=CockpitResponse)
async def get_projet_cockpit(
    projet_id: UUID,  # CORRECTION : UUID au lieu de str
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lecture des données via l'ORM.
    Vérifie que le projet appartient bien à l'utilisateur connecté.
    """

    # 1. Récupération du projet
    projet = db.query(Projet).filter(
        Projet.id == projet_id,
        Projet.user_id == current_user.id
    ).first()
    
    if not projet:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    # 2. Agrégation des données financières
    devis = db.query(Devis).filter(Devis.projet_id == projet.id).all()
    
    budget = sum(d.budget_initial_ht for d in devis)
    debourse = sum(d.cout_total for d in devis)
    vente = sum(d.total_ht for d in devis)
    marge = vente - debourse
    marge_pct = (marge / vente * 100) if vente > 0 else 0.0

    # 3. Alertes et Décisions
    alertes = db.query(Alerte).filter(Alerte.projet_id == projet.id).all()
    decisions = db.query(Decision).filter(Decision.projet_id == projet.id).all()
    
    # 4. Avancement
    avancement = db.query(Avancement).filter(Avancement.projet_id == projet.id).first()

    return CockpitResponse(
        projet=ProjectInfo(id=str(projet.id), nom=projet.nom),
        financials=Financials(
            budget=budget,
            debourse=debourse,
            vente=vente,
            marge=marge,
            marge_pct=round(marge_pct, 2)
        ),
        risque=RiskInfo(exposition=0.0),
        avancement=ProgressInfo(pourcentage=avancement.pourcentage if avancement else 0.0),
        alertes=[AlertInfo(id=a.id, niveau=a.niveau, message=a.message) for a in alertes],
        decisions=[DecisionInfo(id=d.id, date=d.date.isoformat(), action=d.action) for d in decisions],
        updated_at=datetime.now(timezone.utc).isoformat()
    )
