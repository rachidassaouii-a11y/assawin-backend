from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db
from app.routers import auth

app = FastAPI(
    title="ASSAWIN BTP API",
    version="1.0.0",
    description="API Backend pour la gestion de chantiers et chiffrage inversé"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(auth.router)

@app.get("/")
def root():
return {"status": "ok", "message": "ASSAWIN API est opérationnelle 🚀"}




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
