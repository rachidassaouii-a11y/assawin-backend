from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import des routeurs
from projets import router as projets_router
from devis import router as devis_router
from dashboard import router as dashboard_router


app = FastAPI(
    title="ASSAWIN BTP Backend API",
    version="1.1.0",
    description=(
        "Noyau de calcul, gestion des projets, devis, "
        "dashboard et protection des marges."
    )
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTEURS API
# ============================================================

# Projets + Cockpit
app.include_router(projets_router)

# Devis + moteur de calcul
app.include_router(devis_router)

# Dashboard global
app.include_router(dashboard_router)


# ============================================================
# ROUTES SYSTÈME
# ============================================================

@app.get("/")
def read_root():
    return {
        "message": "API ASSAWIN BTP en ligne",
        "status": "active",
        "version": "1.1.0"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "assawin-backend"
    }