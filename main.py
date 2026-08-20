from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db

# Imports des routeurs
from app.routers.truthgate import router as truthgate_router
from app.routers.devis import router as devis_router
from app.routers.projets import router as projets_router
from app.routers.dashboard import router as dashboard_router

app = FastAPI(
    title="Assawin Backend API",
    description="API Backend pour l'écosystème Assawin",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(truthgate_router)
app.include_router(devis_router)
app.include_router(projets_router)
app.include_router(dashboard_router)

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Assawin API Running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
