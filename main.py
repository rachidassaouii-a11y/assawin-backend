from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Assawin Backend API",
    description="API Backend pour l'écosystème Assawin BTP",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---
class TruthGateCheckRequest(BaseModel):
    id_devis: str

class TruthGateIssue(BaseModel):
    code: str
    severity: str
    message: str

class TruthGateResponse(BaseModel):
    score: int
    can_send: bool
    blocking_count: int
    warning_count: int
    issues: List[TruthGateIssue]


# --- ROUTES PRINCIPALES ---
@app.get("/", tags=["Système"])
def read_root():
    return {"status": "ok", "message": "Assawin API Running"}

@app.get("/health", tags=["Système"])
def health_check():
    return {"status": "healthy"}


# --- ROUTE DASHBOARD (Pour ton CodePen) ---
@app.get("/api/v1/dashboard/summary", tags=["Dashboard & Marges"])
def get_dashboard_summary():
    return {
        "nombre_devis": 5,
        "chantiers_en_cours": 2,
        "chiffre_affaires_signe": 28500.0
    }


# --- ROUTES TRUTH GATE & DEVIS ---
@app.post("/api/v1/truthgate/validate", response_model=TruthGateResponse, tags=["Truth Gate"])
def validate_devis(payload: TruthGateCheckRequest):
    return TruthGateResponse(
        score=85,
        can_send=True,
        blocking_count=0,
        warning_count=1,
        issues=[
            TruthGateIssue(
                code="LOW_MARGIN_WARNING",
                severity="WARNING",
                message="Marge à 25%. Recommandation : viser au moins 30%."
            )
        ]
    )

@app.get("/api/v1/devis/{id_devis}/pdf-preview", tags=["Devis"])
def get_pdf_preview(id_devis: str):
    return {
        "reference": f"DEV-{id_devis[:8]}",
        "montant_ht": 12000.0,
        "tva_pct": 20.0,
        "montant_ttc": 14400.0,
        "status": "BROUILLON"
    }

@app.post("/api/v1/projets/convert/{id_devis}", tags=["Projets"])
def convert_devis_to_projet(id_devis: str):
    return {
        "status": "success",
        "message": "Chantier créé avec succès",
        "id_projet": "proj-123456"
    }
