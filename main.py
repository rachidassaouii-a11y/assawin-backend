from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import init_db
from app.routers import auth, chiffrage, passport

app = FastAPI(title="ASSAWIN API")

# Configuration CORS
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

@app.get("/")
def root():
    return {"status": "ok", "message": "ASSAWIN API est opérationnelle 🚀"}

# Routeurs
app.include_router(auth.router)
app.include_router(chiffrage.router)
app.include_router(passport.router)
