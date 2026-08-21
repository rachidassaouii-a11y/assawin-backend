from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard & Marges"])

@router.get("/summary")
def get_dashboard_summary():
    return {
        "nombre_devis": 5,
        "chantiers_en_cours": 2,
        "chiffre_affaires_signe": 28500.0
    }
