from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.all_models import Devis, Projet, User

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard & Marges"])

@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Total des devis
    total_devis = db.query(Devis).filter(Devis.id_user == current_user.id_user).count()
    
    # Total des chantiers en cours
    total_projets = db.query(Projet).filter(Projet.id_user == current_user.id_user).count()

    # Cumul du chiffre d'affaires signé
    ca_total = db.query(func.sum(Devis.montant_total_ht)).filter(
        Devis.id_user == current_user.id_user,
        Devis.statut == "SIGNE"
    ).scalar() or 0.0

    return {
        "nombre_devis": total_devis,
        "chantiers_en_cours": total_projets,
        "chiffre_affaires_signe": float(ca_total)
    }
