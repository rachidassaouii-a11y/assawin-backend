from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1/devis", tags=["Devis & Transaction"])

@router.get("/{id_devis}/pdf-preview")
def get_pdf_preview(id_devis: str):
    return {
        "reference": f"DEV-{id_devis[:8]}",
        "montant_ht": 12000.0,
        "tva_pct": 20.0,
        "montant_ttc": 14400.0,
        "status": "BROUILLON"
    }

@router.post("/{id_devis}/send")
def send_devis_to_client(id_devis: str):
    return {"status": "success", "message": "Devis envoyé au client avec succès"}
