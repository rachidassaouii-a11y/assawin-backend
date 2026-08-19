import os
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_db, SessionLocal
from app.routers import auth, chiffrage, passport
from app.workers.chiffrage_worker import run_periodic_recalculation

# =============== Lifecycle (Gestion du Démarrage/Arrêt) ===============
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Création des tables en BDD au démarrage
    print("🔧 Initialisation de la base de données PostgreSQL...")
    init_db()

    # 2. Lancement du worker d'arrière-plan (Recalcul automatique)
    print("🚀 Démarrage du worker d'arrière-plan (Chiffrage & Passport)...")
    worker_thread = threading.Thread(
        target=run_periodic_recalculation,
        args=(SessionLocal,),
        daemon=True
    )
    worker_thread.start()

    yield  # L'application FastAPI tourne et accepte des requêtes

    print("🛑 Arrêt propre de l'application...")

# =============== Instance FastAPI ===============
app = FastAPI(
    title="ASSAWIN OS Core API",
    description="Moteur économique BTP, Chiffrage Inversé, Passport Engine et Auth JWT",
    version="1.0.0",
    lifespan=lifespan
)

# =============== Configuration CORS ===============
# Autorise les requêtes provenant du Front-End (Wallet, CodePen, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============== Inclusion des Routeurs ===============
app.include_router(auth.router)
app.include_router(chiffrage.router)
app.include_router(passport.router)

# =============== Endpoints Globaux ===============
@app.get("/", tags=["Root"])
def read_root():
    return {
        "service": "ASSAWIN OS Engine API",
        "status": "online",
        "docs": "/docs"
    }

@app.get("/health", tags=["Healthcheck"])
def health_check():
    return {
        "status": "ok",
        "service": "ASSAWIN OS Core API",
        "version": "1.0.0"
    }

# =============== Point d'entrée exécution directe ===============
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
