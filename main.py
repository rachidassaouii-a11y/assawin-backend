from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth import router as auth_router

# On ignore volontairement les autres imports (projets, devis, db) pour éviter le crash 500
# from app.core.database import engine
# from app.models.all_models import Base
# from projets import router as projets_router
# from devis import router as devis_router
# from app.routers.dashboard import router as dashboard_router

app = FastAPI(
    title="ASSAWIN BTP Backend API",
    version="1.0.0",
    description="ASSAWIN — Noyau de calcul, gestion des projets, devis, marges et pilotage métier."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion du routeur Auth uniquement
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "API ASSAWIN BTP en ligne", "status": "active", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "assawin-backend"}