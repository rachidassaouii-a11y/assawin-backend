from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base
from app.models import all_models  # Import défensif déclenchant l'enregistrement des tables

# Import des routeurs à la racine
import auth
import projets
import devis
import dashboard
import wallet
import next_best_action

# Création automatique de la structure de tables PostgreSQL/SQLite
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ASSAWIN BTP API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://rachidassaouii-a11y.github.io",
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(projets.router, prefix="/api/v1/projets", tags=["Projets / Cockpit"])
app.include_router(devis.router, prefix="/api/v1/devis", tags=["Devis"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(wallet.router, prefix="/api/v1/wallet", tags=["Wallet"])
app.include_router(next_best_action.router, prefix="/api/v1/nba", tags=["Next Best Action"])
