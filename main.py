from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.database import engine
from app.models.all_models import Base

from projets import router as projets_router
from devis import router as devis_router
from app.routers.dashboard import router as dashboard_router
from app.routers.photos import router as photos_router
from app.routers.comptes_rendus import router as comptes_rendus_router
from app.routers.notifications import router as notifications_router
from app.routers.clients import router as clients_router
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


# ============================================================
# CRÉATION DES TABLES MANQUANTES
# ============================================================

# Base SQLAlchemy utilisée par tous les modèles ASSAWIN
Base.metadata.create_all(bind=engine)


# ============================================================
# MIGRATION AUTOMATIQUE
# Ajoute les colonnes manquantes à la table projets
# ============================================================

with engine.connect() as conn:

    conn.execute(
        text(
            "ALTER TABLE projets "
            "ADD COLUMN IF NOT EXISTS adresse VARCHAR"
        )
    )

    conn.execute(
        text(
            "ALTER TABLE projets "
            "ADD COLUMN IF NOT EXISTS description VARCHAR"
        )
    )

    conn.execute(
        text(
            "ALTER TABLE projets "
            "ADD COLUMN IF NOT EXISTS client_id VARCHAR(36)"
        )
    )

    conn.execute(
        text(
            "ALTER TABLE projets "
            "ADD COLUMN IF NOT EXISTS marge_cible_pct FLOAT DEFAULT 30.0"
        )
    )

    conn.execute(
        text(
            "ALTER TABLE projets "
            "ADD COLUMN IF NOT EXISTS statut VARCHAR DEFAULT 'EN_COURS'"
        )
    )

    conn.commit()


# ============================================================
# ROUTERS
# ============================================================

app.include_router(auth_router)
app.include_router(projets_router)
app.include_router(devis_router)
app.include_router(dashboard_router)
app.include_router(photos_router)
app.include_router(comptes_rendus_router)
app.include_router(notifications_router)
app.include_router(clients_router)


# ============================================================
# ROUTES SYSTÈME
# ============================================================

@app.get("/")
def read_root():
    return {
        "message": "API ASSAWIN BTP en ligne",
        "status": "active",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "assawin-backend"
    }
