"""
dashboard.py — Routeur pour les KPIs du Command Center
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])
security = HTTPBearer()

# Mock data
_devis_mock = [
    {"id": 1, "reference": "DEV-001", "client": "Dupont", "montant_ht": 1200, "statut": "en_cours"},
    {"id": 2, "reference": "DEV-002", "client": "Martin", "montant_ht": 800, "statut": "en_cours"},
    {"id": 3, "reference": "DEV-003", "client": "Bernard", "montant_ht": 0, "statut": "brouillon"},
]

_projets_mock = [
    {"id": 1, "nom": "Chantier A", "statut": "actif"},
    {"id": 2, "nom": "Chantier B", "statut": "actif"},
]

def _get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    if token.credentials != "fake-token":
        raise HTTPException(status_code=401, detail="Token invalide")
    return {"user_id": 1, "email": "test@assawin.com"}

@router.get("/summary")
def get_dashboard_summary(user: dict = Depends(_get_current_user)):
    devis_en_cours = [d for d in _devis_mock if d["statut"] == "en_cours"]
    ca_total = sum(d["montant_ht"] for d in devis_en_cours)
    return {
        "devis_en_cours": len(devis_en_cours),
        "projets_actifs": len([p for p in _projets_mock if p["statut"] == "actif"]),
        "ca_total": ca_total,
        "marge_totale": ca_total * 0.40,
        "taux_marge": 40.0,
        "alertes": [
            {"type": "warning", "message": "Devis DEV-001 : marge inférieure à la cible"},
            {"type": "info", "message": "Projet B : échéance dans 3 jours"}
        ]
    }

@router.get("/kpis")
def get_kpis(user: dict = Depends(_get_current_user)):
    devis_en_cours = [d for d in _devis_mock if d["statut"] == "en_cours"]
    ca_total = sum(d["montant_ht"] for d in devis_en_cours)
    return {
        "devis_en_cours": len(devis_en_cours),
        "projets_actifs": len([p for p in _projets_mock if p["statut"] == "actif"]),
        "ca_total": ca_total,
        "signatures_en_attente": 3,
        "fournisseurs_actifs": 24,
        "score_moyen_portfolio": 82
    }