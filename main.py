from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth

app = FastAPI(
    title="Assawin BTP API",
    version="1.0.0",
    description="API backend pour la gestion de chantier et devis Assawin"
)

# Configuration CORS pour autoriser toutes les connexions (Swagger, frontend, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrement des routes d'authentification
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "Assawin BTP Backend",
        "docs": "/docs"
    }
        
        return {
            "access_token": encoded_jwt,
            "token_type": "bearer"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne: {str(e)}"
        )

# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTEURS
# ============================================================

app.include_router(auth_router)
app.include_router(projets_router)
app.include_router(devis_router)
app.include_router(dashboard_router)


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
