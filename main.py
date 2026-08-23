import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, projets, devis, dashboard, wallet
from app.core.database import engine
from app.models import all_models

all_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ASSAWIN™ BTP API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration explicite du préfixe /api/v1/projets
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentification"])
app.include_router(projets.router, prefix="/api/v1/projets", tags=["Projets"])
app.include_router(devis.router, prefix="/api/v1/devis", tags=["Devis"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(wallet.router, prefix="/api/v1/wallet", tags=["Wallet"])

@app.get("/", tags=["Système"])
async def root():
    return {"status": "online", "app": "ASSAWIN API"}

@app.get("/health", tags=["Système"])
async def health_check():
    return {"status": "ok"}
