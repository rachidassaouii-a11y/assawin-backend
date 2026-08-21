from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/projets", tags=["Chantiers & Projets"])

@router.post("/convert/{id_devis}")
def convert_devis_to_projet(id_devis: str):
    return {
        "status": "success",
        "message": "Chantier créé avec succès",
        "id_projet": "proj-123456"
    }
