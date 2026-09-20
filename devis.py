import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.all_models import Devis, Projet, Client, User


router = APIRouter(
    prefix="/api/v1/devis",
    tags=["Devis & Calculs"]
)

TRUTH_GATE_MIN_TAUX_MARQUE = 20.0


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
    lots: List[LotDevisCreate] = Field(..., min_length=1)
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
    can_send: bool


class DevisPersistedResponse(DevisResponse):
    id_devis: str
    id_projet: str
    statut: str
    reference: str
    numero_devis: Optional[str] = None
    numero_facture: Optional[str] = None


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

    taux_rendement_cout_pct = round(
        (marge_brute_eur / cout_total) * 100, 2
    ) if cout_total > 0 else 0.0

    taux_marque_pct = round(
        (marge_brute_eur / total_ht) * 100, 2
    ) if total_ht > 0 else 0.0

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


def _totaux_depuis_devis_persiste(devis: Devis) -> dict:
    """Reconstruit le dict de calculs à partir des SEULES colonnes
    réellement persistées sur l'objet Devis. N'invente aucun taux :
    marge_brute_eur / taux_rendement_cout_pct / taux_marque_pct restent
    des ratios dérivés de total_ht et cout_total (déjà persistés et
    fiables), jamais de constantes forcées."""
    total_ht = float(devis.total_ht or 0.0)
    cout_total = float(devis.cout_total or 0.0)
    total_tva = float(devis.total_tva or 0.0)
    total_ttc = float(devis.total_ttc or 0.0)
    acompte_montant = float(devis.acompte_montant or 0.0)

    marge_brute_eur = round(total_ht - cout_total, 2)

    taux_rendement_cout_pct = round(
        (marge_brute_eur / cout_total) * 100, 2
    ) if cout_total > 0 else 0.0

    taux_marque_pct = round(
        (marge_brute_eur / total_ht) * 100, 2
    ) if total_ht > 0 else 0.0

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


def _evaluer_truth_gate(calculs: dict, fournisseur_non_verifie: bool) -> dict:
    warnings = []

    if fournisseur_non_verifie:
        warnings.append("Fournisseur non vérifié")

    if calculs["total_ht"] <= 0:
        warnings.append("Le total HT doit être supérieur à zéro")

    if calculs["taux_marque_pct"] < TRUTH_GATE_MIN_TAUX_MARQUE:
        warnings.append(
            f"Taux de marque faible : {calculs['taux_marque_pct']}% "
            f"(seuil minimum : {TRUTH_GATE_MIN_TAUX_MARQUE}%)"
        )

    can_send = (
        calculs["total_ht"] > 0
        and calculs["taux_marque_pct"] >= TRUTH_GATE_MIN_TAUX_MARQUE
    )

    return {"warnings": warnings, "can_send": can_send}


def _extraire_suffixe_client(numero_client: Optional[str]) -> str:
    if numero_client and "-" in numero_client:
        return numero_client.split("-", 1)[1]
    return "0000"


def _generer_numero_devis(db: Session, projet: Projet, current_user_id: str) -> str:
    if projet.client_id:
        client = db.query(Client).filter(Client.id == projet.client_id).first()
        suffixe_client = _extraire_suffixe_client(
            getattr(client, "numero_client", None) if client else None
        )
        nombre_devis_client = (
            db.query(Devis)
            .join(Projet, Devis.projet_id == Projet.id)
            .filter(Projet.client_id == projet.client_id)
            .count()
        )
    else:
        suffixe_client = "0000"
        nombre_devis_client = (
            db.query(Devis)
            .join(Projet, Devis.projet_id == Projet.id)
            .filter(Projet.client_id.is_(None), Projet.user_id == current_user_id)
            .count()
        )

    compteur = nombre_devis_client + 1
    return f"DEV-{suffixe_client}-{compteur:02d}"


@router.get("/", response_model=List[DevisPersistedResponse])
def lister_devis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    devis_list = (
        db.query(Devis)
        .join(Projet, Devis.projet_id == Projet.id)
        .filter(Projet.user_id == str(current_user.id))
        .all()
    )

    result = []

    for d in devis_list:
        calculs = _totaux_depuis_devis_persiste(d)
        truth_gate = _evaluer_truth_gate(calculs, bool(d.fournisseur_non_verifie))

        result.append({
            "id_devis": str(d.id),
            "id_projet": str(d.projet_id),
            "statut": d.statut or "BROUILLON",
            "reference": d.reference or "Devis",
            "numero_devis": d.numero_devis,
            "numero_facture": d.numero_facture,
            **calculs,
            **truth_gate,
        })

    return result


@router.post("/calculate", response_model=DevisResponse)
def calculate_devis(
    data: DevisCalculateRequest,
    current_user: User = Depends(get_current_user)
):
    calculs = _calculer_totaux_devis(data.lots, data.acompte_pct)
    truth_gate = _evaluer_truth_gate(calculs, data.fournisseur_non_verifie)

    return {**calculs, **truth_gate}


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=DevisPersistedResponse)
def create_and_persist_devis(
    data: DevisCalculateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not data.id_projet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="id_projet obligatoire pour persister un devis"
        )

    try:
        uuid.UUID(data.id_projet)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format id_projet UUID invalide"
        )

    projet = (
        db.query(Projet)
        .filter(
            Projet.id == data.id_projet,
            Projet.user_id == str(current_user.id)
        )
        .first()
    )

    if not projet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projet introuvable ou non autorisé"
        )

    calculs = _calculer_totaux_devis(data.lots, data.acompte_pct)
    truth_gate = _evaluer_truth_gate(calculs, data.fournisseur_non_verifie)
    numero_devis = _generer_numero_devis(db, projet, str(current_user.id))

    nouveau_devis = Devis(
        id=str(uuid.uuid4()),
        projet_id=str(projet.id),
        total_ht=calculs["total_ht"],
        cout_total=calculs["cout_total"],
        total_tva=calculs["total_tva"],
        total_ttc=calculs["total_ttc"],
        acompte_montant=calculs["acompte_montant"],
        acompte_pct=data.acompte_pct,
        statut="BROUILLON",
        reference=data.titre.strip(),
        fournisseur_non_verifie=data.fournisseur_non_verifie,
        numero_devis=numero_devis,
        created_at=datetime.now(timezone.utc),
    )

    db.add(nouveau_devis)
    db.commit()
    db.refresh(nouveau_devis)

    return {
        "id_devis": str(nouveau_devis.id),
        "id_projet": str(nouveau_devis.projet_id),
        "statut": nouveau_devis.statut,
        "reference": nouveau_devis.reference,
        "numero_devis": nouveau_devis.numero_devis,
        "numero_facture": nouveau_devis.numero_facture,
        **calculs,
        **truth_gate,
    }


@router.put("/{id_devis}", response_model=DevisPersistedResponse)
def update_devis(
    id_devis: str,
    data: DevisCalculateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        uuid.UUID(id_devis)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format id_devis UUID invalide"
        )

    devis = (
        db.query(Devis)
        .join(Projet, Devis.projet_id == Projet.id)
        .filter(
            Devis.id == id_devis,
            Projet.user_id == str(current_user.id)
        )
        .first()
    )

    if not devis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Devis introuvable ou non autorisé"
        )

    calculs = _calculer_totaux_devis(data.lots, data.acompte_pct)
    truth_gate = _evaluer_truth_gate(calculs, data.fournisseur_non_verifie)

    devis.total_ht = calculs["total_ht"]
    devis.cout_total = calculs["cout_total"]
    devis.total_tva = calculs["total_tva"]
    devis.total_ttc = calculs["total_ttc"]
    devis.acompte_montant = calculs["acompte_montant"]
    devis.acompte_pct = data.acompte_pct
    devis.reference = data.titre.strip()
    devis.fournisseur_non_verifie = data.fournisseur_non_verifie
    # Le statut n'est pas modifié ici : DevisCalculateRequest ne porte
    # pas de champ statut, on ne touche donc pas à celui déjà persisté.

    if not devis.numero_devis:
        projet = db.query(Projet).filter(Projet.id == devis.projet_id).first()
        if projet:
            devis.numero_devis = _generer_numero_devis(db, projet, str(current_user.id))

    db.commit()
    db.refresh(devis)

    return {
        "id_devis": str(devis.id),
        "id_projet": str(devis.projet_id),
        "statut": devis.statut or "BROUILLON",
        "reference": devis.reference or "Devis",
        "numero_devis": devis.numero_devis,
        "numero_facture": devis.numero_facture,
        **calculs,
        **truth_gate,
    }


@router.put("/{id_devis}/facturer", response_model=DevisPersistedResponse)
def facturer_devis(
    id_devis: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        uuid.UUID(id_devis)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format id_devis UUID invalide"
        )

    devis = (
        db.query(Devis)
        .join(Projet, Devis.projet_id == Projet.id)
        .filter(
            Devis.id == id_devis,
            Projet.user_id == str(current_user.id)
        )
        .first()
    )

    if not devis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Devis introuvable ou non autorisé"
        )

    if devis.numero_facture:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ce devis est déjà facturé sous le numéro {devis.numero_facture}"
        )

    if not devis.numero_devis:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce devis n'a pas de numéro de devis, impossible de générer une facture"
        )

    devis.numero_facture = devis.numero_devis.replace("DEV-", "FAC-", 1)
    devis.statut = "FACTURE"
    db.commit()
    db.refresh(devis)

    calculs = _totaux_depuis_devis_persiste(devis)
    truth_gate = _evaluer_truth_gate(calculs, bool(devis.fournisseur_non_verifie))

    return {
        "id_devis": str(devis.id),
        "id_projet": str(devis.projet_id),
        "statut": devis.statut or "BROUILLON",
        "reference": devis.reference or "Devis",
        "numero_devis": devis.numero_devis,
        "numero_facture": devis.numero_facture,
        **calculs,
        **truth_gate,
    }


@router.delete("/{id_devis}")
def delete_devis(
    id_devis: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        uuid.UUID(id_devis)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format id_devis UUID invalide"
        )

    devis = (
        db.query(Devis)
        .join(Projet, Devis.projet_id == Projet.id)
        .filter(
            Devis.id == id_devis,
            Projet.user_id == str(current_user.id)
        )
        .first()
    )

    if not devis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Devis introuvable ou non autorisé"
        )

    db.delete(devis)
    db.commit()

    return {"message": "Devis supprimé avec succès"}
