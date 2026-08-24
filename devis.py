from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.all_models import Devis, Projet, User

router = APIRouter(prefix="/api/v1/devis", tags=["Devis & Calculs"])

# ===== SCHÉMAS PYDANTIC =====

class LigneDevisCreate(BaseModel):
    designation: str = Field(..., min_length=1)
    unite: str = Field(..., min_length=1)
    quantite: float = Field(..., gt=0)
    prix_unitaire_ht: float = Field(..., ge=0)
    debourse_sec_unitaire: float = Field(..., ge=0)
    taux_tva: float = Field(20.0, ge=0)

class LotDevisCreate(BaseModel):
    nom_lot: str = Field(..., min_length=1)
    lignes: List[LigneDevisCreate]

class DevisCalculateRequest(BaseModel):
    titre: str = Field(..., min_length=1)
    acompte_pct: float = Field(30.0, ge=0, le=100)
    lots: List[LotDevisCreate]
    id_projet: Optional[str] = None
    marge_cible_pct: float = Field(30.0, ge=0, le=100)
    fournisseur_non_verifie: bool = False

class DevisResponse(BaseModel):
    total_ht: float
    cout_total: float
    total_tva: float
    total_ttc: float
    marge_brute_eur: float
    taux_rendement_cout_pct: float
    taux_marque_pct: float
    acompte_montant: float
    warnings: List[str]


# ===== MOTEUR DE CALCUL CENTRAL =====

def _calculer_totaux_devis(lots: List[LotDevisCreate], acompte_pct: float) -> dict:
    total_ht = 0.0
    cout_total = 0.0
    total_tva = 0.0

    for lot in lots:
        for ligne in lot.lignes:
            ligne_ht = ligne.quantite * ligne.prix_unitaire_ht
            ligne_cout = ligne.quantite * ligne.debourse_sec_unitaire
            ligne_tva = ligne_ht * (ligne.taux_tva / 100.0)

            total_ht += ligne_ht
            cout_total += ligne_cout
            total_tva += ligne_tva

    total_ht = round(total_ht, 2)
    cout_total = round(cout_total, 2)
    total_tva = round(total_tva, 2)
    total_ttc = round(total_ht + total_tva, 2)

    marge_brute_eur = round(total_ht - cout_total, 2)
    taux_rendement_cout_pct = round((marge_brute_eur / cout_total) * 100, 2) if cout_total > 0 else 0.0
    taux_marque_pct = round((marge_brute_eur / total_ht) * 100, 2) if total_ht > 0 else 0.0
    acompte_montant = round(total_ttc * (acompte_pct / 100.0), 2)

    return {
        "total_ht": total_ht,
        "cout_total": cout_total,
        "total_tva": total_tva,
        "total_ttc": total_ttc,
        "marge_brute_eur": marge_brute_eur,
        "taux_rendement_cout_pct": taux_rendement_cout_pct,
        "taux_marque_pct": taux_marque_pct,
        "acompte_montant": acompte_montant,
    }


# ===== ENDPOINTS =====

@router.post("/calculate", response_model=DevisResponse)
def calculate_devis(
    data: DevisCalculateRequest,
    current_user: User = Depends(get_current_user)
):
    calculs = _calculer_totaux_devis(data.lots, data.acompte_pct)
    
    warnings = []
    if data.fournisseur_non_verifie:
        warnings.append("Fournisseur non vérifié")
    if calculs["taux_marque_pct"] < 20.0:
        warnings.append(f"Taux de marque faible : {calculs['taux_marque_pct']}% (Seuil recommandé: 20%)")

    return {
        **calculs,
        "warnings": warnings
    }


@router.post("/", status_code=201)
def create_and_persist_devis(
    data: DevisCalculateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not data.id_projet:
        raise HTTPException(status_code=400, detail="id_projet obligatoire pour persister un devis")

    try:
        proj_uuid = uuid.UUID(data.id_projet)
    except ValueError:
        raise HTTPException(status_code=400, detail="Format id_projet UUID invalide")

    projet = db.query(Projet).filter(
        Projet.id_projet == proj_uuid,
        Projet.id_user == current_user.id_user
    ).first()
    if not projet:
        raise HTTPException(status_code=404, detail="Projet introuvable ou non autorisé")

    calculs = _calculer_totaux_devis(data.lots, data.acompte_pct)

    nouveau_devis = Devis(
        id_devis=uuid.uuid4(),
        id_projet=projet.id_projet,
        reference=data.titre,
        total_ht=calculs["total_ht"],
        cout_total=calculs["cout_total"],
        marge_cible_pct=data.marge_cible_pct,
        fournisseur_non_verifie=data.fournisseur_non_verifie,
        date_creation=datetime.now(timezone.utc)
    )

    db.add(nouveau_devis)
    db.commit()
    db.refresh(nouveau_devis)

    return {
        "id_devis": str(nouveau_devis.id_devis),
        "reference": nouveau_devis.reference,
        **calculs,
        "warnings": ["Fournisseur non vérifié"] if nouveau_devis.fournisseur_non_verifie else []
    }
