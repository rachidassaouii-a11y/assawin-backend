from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/devis", tags=["Devis"])

class LigneDevis(BaseModel):
    designation: str
    unite: str  # m², m³, ml, u, f, h
    quantite: float
    prix_unitaire_ht: float
    debourse_sec_unitaire: float  # Coût réel matériel + MO
    taux_tva: float = 20.0

class LotDevis(BaseModel):
    nom_lot: str
    lignes: List[LigneDevis]

class DevisCalculateRequest(BaseModel):
    titre: str
    acompte_pct: float = 30.0
    lots: List[LotDevis]

class IssueTruthGate(BaseModel):
    code: str
    severity: str  # BLOCKING ou WARNING
    message: str

class DevisCalculatedResponse(BaseModel):
    total_ht: float
    total_tva: float
    total_ttc: float
    acompte_montant: float
    debourse_sec_total: float
    marge_brute_eur: float
    taux_marge_pct: float
    can_send: bool
    truth_gate_issues: List[IssueTruthGate]

@router.post("/calculate", response_model=DevisCalculatedResponse)
async def calculate_and_validate_devis(payload: DevisCalculateRequest):
    total_ht = 0.0
    total_tva = 0.0
    debourse_sec_total = 0.0
    issues: List[IssueTruthGate] = []

    if payload.acompte_pct <= 0:
        issues.append(IssueTruthGate(
            code="NO_DOWN_PAYMENT",
            severity="WARNING",
            message="Aucun acompte renseigné (30% recommandé par défaut)."
        ))

    for lot in payload.lots:
        for ligne in lot.lignes:
            ht_ligne = ligne.quantite * ligne.prix_unitaire_ht
            debourse_ligne = ligne.quantite * ligne.debourse_sec_unitaire
            
            total_ht += ht_ligne
            total_tva += ht_ligne * (ligne.taux_tva / 100.0)
            debourse_sec_total += debourse_ligne

            if ligne.quantite > 0 and ligne.prix_unitaire_ht == 0:
                issues.append(IssueTruthGate(
                    code="ZERO_PRICE_LINE",
                    severity="BLOCKING",
                    message=f"La ligne '{ligne.designation}' a une quantité sans prix unitaire HT."
                ))

    total_ttc = total_ht + total_tva
    acompte_montant = total_ttc * (payload.acompte_pct / 100.0)
    
    marge_brute_eur = total_ht - debourse_sec_total
    taux_marge_pct = (marge_brute_eur / total_ht * 100.0) if total_ht > 0 else 0.0

    if total_ht > 0 and taux_marge_pct < 20.0:
        issues.append(IssueTruthGate(
            code="CRITICAL_LOW_MARGIN",
            severity="BLOCKING",
            message=f"Marge brute de {taux_marge_pct:.1f}% inférieure au seuil critique de 20%."
        ))
    elif 20.0 <= taux_marge_pct < 30.0:
        issues.append(IssueTruthGate(
            code="WARNING_LOW_MARGIN",
            severity="WARNING",
            message=f"Marge brute à {taux_marge_pct:.1f}%. Objectif recommandé : >= 30%."
        ))

    has_blocking = any(issue.severity == "BLOCKING" for issue in issues)

    return DevisCalculatedResponse(
        total_ht=round(total_ht, 2),
        total_tva=round(total_tva, 2),
        total_ttc=round(total_ttc, 2),
        acompte_montant=round(acompte_montant, 2),
        debourse_sec_total=round(debourse_sec_total, 2),
        marge_brute_eur=round(marge_brute_eur, 2),
        taux_marge_pct=round(taux_marge_pct, 1),
        can_send=not has_blocking,
        truth_gate_issues=issues
    )
