from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.all_models import Projet, Devis, User

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Dashboard & Marges"]
)


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Synthèse globale réelle de l'activité de l'utilisateur connecté.

    Agrège les projets et devis appartenant à l'utilisateur.
    Aucune donnée financière n'est simulée.
    """

    projets = (
        db.query(Projet)
        .filter(Projet.user_id == str(current_user.id))
        .all()
    )

    projet_ids = [str(projet.id) for projet in projets]

    if not projet_ids:
        return {
            "nombre_projets": 0,
            "chantiers_en_cours": 0,
            "nombre_devis": 0,
            "chiffre_affaires_total": 0.0,
            "cout_total": 0.0,
            "marge_brute_eur": 0.0,
            "taux_marque_pct": 0.0
        }

    devis = (
        db.query(Devis)
        .filter(Devis.projet_id.in_(projet_ids))
        .all()
    )

    chiffre_affaires_total = round(
        sum(float(devis_item.total_ht or 0.0) for devis_item in devis),
        2
    )

    cout_total = round(
        sum(float(devis_item.cout_total or 0.0) for devis_item in devis),
        2
    )

    marge_brute_eur = round(
        chiffre_affaires_total - cout_total,
        2
    )

    taux_marque_pct = round(
        (marge_brute_eur / chiffre_affaires_total) * 100,
        2
    ) if chiffre_affaires_total > 0 else 0.0

    return {
        "nombre_projets": len(projets),
        "chantiers_en_cours": len(projets),
        "nombre_devis": len(devis),
        "chiffre_affaires_total": chiffre_affaires_total,
        "cout_total": cout_total,
        "marge_brute_eur": marge_brute_eur,
        "taux_marque_pct": taux_marque_pct
    }