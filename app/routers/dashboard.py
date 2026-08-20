from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard & Marges"])

@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Endpoint temporaire sécurisé pour valider le chargement
    return {
        "nombre_devis": 3,
        "chantiers_en_cours": 1,
        "chiffre_affaires_signe": 14500.0
    }
