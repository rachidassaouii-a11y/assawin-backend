from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db

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

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Assawin API Running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
