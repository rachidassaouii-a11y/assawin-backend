from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine
from app.models.all_models import Base  # la VRAIE Base — celle où les modèles sont réellement enregistrés

from projets import router as projets_router
from devis import router as devis_router
from app.routers.dashboard import router as dashboard_router
from app.routers.auth import router as auth_router

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