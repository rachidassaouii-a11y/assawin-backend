import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Imports des routeurs
from app.routers import auth, projets, devis, dashboard, wallet
from app.core.database import engine
from app.models import all_models

# Création automatique des tables
all_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ASSAWIN™ BTP API",
    description="Backend SaaS & Mobile ASSAWIN - Management, Marge & Risque BTP",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrement des routeurs
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentification"])
app.include_router(projets.router, prefix="/api/v1/projets", tags=["Projets"])

app.include_router(devis.router, prefix="/api/v1/devis", tags=["Devis"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(wallet.router, prefix="/api/v1/wallet", tags=["Wallet"])

@app.get("/", tags=["Système"])
async def root():
    return {
        "status": "online",
        "app": "ASSAWIN API",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Système"])
async def health_check():
    return {"status": "ok"}

