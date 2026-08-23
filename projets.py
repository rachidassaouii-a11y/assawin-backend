from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.orm import Session
import uuid

# À adapter selon ton fichier de connexion DB
try:
    from main import get_db
except ImportError:
    def get_db():
        raise HTTPException(status_code=500, detail="get_db non configuré")

router = APIRouter(prefix="/api/v1/projets", tags=["Cockpit"])

# --- Schémas Pydantic (Contrat strict) ---
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

# --- Routeur principal (connecté aux vraies tables) ---
@router.get("/{projet_id}/cockpit", response_model=CockpitResponse)
async def get_projet_cockpit(projet_id: str, db: Session = Depends(get_db)):
    """
    Endpoint qui lit les données depuis les tables réelles.
    Ne renvoie JAMAIS de chiffres en dur.
    """
    # 1. Projet (vraies colonnes)
    projet = db.execute(
        text("SELECT id_projet, nom_projet, budget_initial_ht FROM projets WHERE id_projet = :id"), 
        {"id": projet_id}
    ).mappings().first()
    
    if not projet:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    # 2. Finances (agrégées depuis la table devis, vraies colonnes)
    fin_data = db.execute(
        text("""
            SELECT 
                COALESCE(SUM(budget_initial_ht), 0) as budget,
                COALESCE(SUM(cout_total), 0) as debourse,
                COALESCE(SUM(total_ht), 0) as vente
            FROM devis 
            WHERE id_projet = :id
        """), {"id": projet_id}
    ).mappings().first()

    budget = fin_data["budget"]
    debourse = fin_data["debourse"]
    vente = fin_data["vente"]
    marge = vente - debourse
    marge_pct = (marge / vente * 100) if vente > 0 else 0.0

    # 3. Alertes et Décisions (vides pour l'instant, mais présents dans le contrat)
    alertes = []
    decisions = []

    # 4. Avancement (vides pour l'instant, table à créer plus tard)
    avancement = 0.0

    return CockpitResponse(
        projet=ProjectInfo(id=projet["id_projet"], nom=projet["nom_projet"]),
        financials=Financials(
            budget=budget,
            debourse=debourse,
            vente=vente,
            marge=marge,
            marge_pct=round(marge_pct, 2)
        ),
        risque=RiskInfo(exposition=0.0),  # À brancher sur ton Risk Engine
        avancement=ProgressInfo(pourcentage=avancement),
        alertes=alertes,
        decisions=decisions,
        updated_at=datetime.now(timezone.utc).isoformat()
    )
