from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import des routeurs depuis la racine
from projets import router as projets_router
from devis import router as devis_router

app = FastAPI(
    title="ASSAWIN BTP Backend API",
    version="1.0.0",
    description="Noyau de calcul, gestion des projets, devis et vérité des marges."
)

# Configuration CORS pour autoriser l'accès front / tests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion de tous les routeurs opérationnels
app.include_router(projets_router)
app.include_router(devis_router)

@app.get("/")
def read_root():
    return {"message": "API ASSAWIN BTP en ligne", "status": "active"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "assawin-backend"}
