from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime, timezone

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

# --- Simulation temporaire (à remplacer par de vraies requêtes DB quand la base sera connectée) ---
MOCK_PROJETS = {
    "project_001": {
        "nom": "Villa Atlas",
        "budget": 150000.0,
        "debourse": 90000.0,
        "vente": 200000.0
    }
}

# --- Routeur principal ---
@router.get("/{projet_id}/cockpit", response_model=CockpitResponse)
async def get_projet_cockpit(projet_id: str):
    if projet_id not in MOCK_PROJETS:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    data = MOCK_PROJETS[projet_id]
    
    budget = data["budget"]
    debourse = data["debourse"]
    vente = data["vente"]
    marge = vente - debourse
    marge_pct = (marge / vente * 100) if vente > 0 else 0.0

    return CockpitResponse(
        projet=ProjectInfo(id=projet_id, nom=data["nom"]),
        financials=Financials(
            budget=budget, debourse=debourse, vente=vente,
            marge=marge, marge_pct=round(marge_pct, 2)
        ),
        risque=RiskInfo(exposition=0.0),
        avancement=ProgressInfo(pourcentage=0.0),
        alertes=[],
        decisions=[],
        updated_at=datetime.now(timezone.utc).isoformat()
    )
