import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.all_models import Projet, Devis, User

router = APIRouter(prefix="/api/v1/projets", tags=["Projets & Cockpit"])

TRUTH_GATE_MIN_TAUX_MARQUE = 20.0

class ProjetCreate(BaseModel):
    nom_projet: str = Field(..., min_length=1)
    budget_initial_ht: float = Field(0.0, ge=0)
    marge_cible_pct: float = Field(30.0, ge=0, le=100)
    statut: str = Field("EN_COURS")
    description: Optional[str] = None

class ProjetResponse(BaseModel):
    id_projet: str
    nom_projet: str
    budget_initial_ht: float
    marge_cible_pct: float
    statut: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

def _to_float(value) -> float:
    return float(value or 0.0)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProjetResponse)
def create_projet(
    data: ProjetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    nouveau_projet = Projet(
        id_projet=str(uuid.uuid4()),
        id_user=str(current_user.id_user),
        nom_projet=data.nom_projet.strip(),
        budget_initial_ht=data.budget_initial_ht,
        marge_cible_pct=data.marge_cible_pct,
        statut=data.statut,
        description=data.description,
        date_creation=datetime.now(timezone.utc),
    )
    db.add(nouveau_projet)
    db.commit()
    db.refresh(nouveau_projet)
    return nouveau_projet

@router.get("/", response_model=List[ProjetResponse])
def list_projets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Projet)
        .filter(Projet.id_user == str(current_user.id_user))
        .order_by(Projet.date_creation.desc())
        .all()
    )

@router.get("/{projet_id}/cockpit")
def get_projet_cockpit(
    projet_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        uuid.UUID(projet_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format UUID projet invalide"
        )

    projet = (
        db.query(Projet)
        .filter(
            Projet.id_projet == projet_id,
            Projet.id_user == str(current_user.id_user)
        )
        .first()
    )

    if not projet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projet introuvable ou non autorisé"
        )

    devis_list = (
        db.query(Devis)
        .filter(Devis.id_projet == projet.id_projet)
        .all()
    )

    total_devis_ht = round(sum(_to_float(d.total_ht) for d in devis_list), 2)
    total_cout = round(sum(_to_float(d.cout_total) for d in devis_list), 2)
    marge_globale_eur = round(total_devis_ht - total_cout, 2)

    taux_rendement_cout_pct = round(
        (marge_globale_eur / total_cout) * 100, 2
    ) if total_cout > 0 else 0.0

    taux_marque_global = round(
        (marge_globale_eur / total_devis_ht) * 100, 2
    ) if total_devis_ht > 0 else 0.0

    warnings = []
    if total_devis_ht > 0 and taux_marque_global < TRUTH_GATE_MIN_TAUX_MARQUE:
        warnings.append(
            f"Taux de marque global faible : {taux_marque_global}% "
            f"(seuil minimum : {TRUTH_GATE_MIN_TAUX_MARQUE}%)"
mport uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.all_models import Projet, Devis, User

router = APIRouter(prefix="/api/v1/projets", tags=["Projets & Cockpit"])

TRUTH_GATE_MIN_TAUX_MARQUE = 20.0

class ProjetCreate(BaseModel):
    nom_projet: str = Field(..., min_length=1)
    budget_initial_ht: float = Field(0.0, ge=0)
    marge_cible_pct: float = Field(30.0, ge=0, le=100)
    statut: str = Field("EN_COURS")
    description: Optional[str] = None

class ProjetResponse(BaseModel):
    id_projet: str
    nom_projet: str
    budget_initial_ht: float
    marge_cible_pct: float
    statut: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

def _to_float(value) -> float:
    return float(value or 0.0)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProjetResponse)
def create_projet(
    data: ProjetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    nouveau_projet = Projet(
        id_projet=str(uuid.uuid4()),
        id_user=str(current_user.id_user),
        nom_projet=data.nom_projet.strip(),
        budget_initial_ht=data.budget_initial_ht,
        marge_cible_pct=data.marge_cible_pct,
        statut=data.statut,
        description=data.description,
        date_creation=datetime.now(timezone.utc),
    )
    db.add(nouveau_projet)
    db.commit()
    db.refresh(nouveau_projet)
    return nouveau_projet

@router.get("/", response_model=List[ProjetResponse])
def list_projets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Projet)
        .filter(Projet.id_user == str(current_user.id_user))
        .order_by(Projet.date_creation.desc())
        .all()
    )

@router.get("/{projet_id}/cockpit")
def get_projet_cockpit(
    projet_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        uuid.UUID(projet_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format UUID projet invalide"
        )

    projet = (
        db.query(Projet)
        .filter(
            Projet.id_projet == projet_id,
            Projet.id_user == str(current_user.id_user)
        )
        .first()
    )

    if not projet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projet introuvable ou non autorisé"
        )

    devis_list = (
        db.query(Devis)
        .filter(Devis.id_projet == projet.id_projet)
        .all()
    )

    total_devis_ht = round(sum(_to_float(d.total_ht) for d in devis_list), 2)
    total_cout = round(sum(_to_float(d.cout_total) for d in devis_list), 2)
    marge_globale_eur = round(total_devis_ht - total_cout, 2)

    taux_rendement_cout_pct = round(
        (marge_globale_eur / total_cout) * 100, 2
    ) if total_cout > 0 else 0.0

    taux_marque_global = round(
        (marge_globale_eur / total_devis_ht) * 100, 2
    ) if total_devis_ht > 0 else 0.0

    warnings = []
    if total_devis_ht > 0 and taux_marque_global < TRUTH_GATE_MIN_TAUX_MARQUE:
        warnings.append(
            f"Taux de marque global faible : {taux_marque_global}% "
            f"(seuil minimum : {TRUTH_GATE_MIN_TAUX_MARQUE}%)"
        )

    return {
        "id_projet": str(projet.id_projet),
        "nom_projet": projet.nom_projet,
        "statut": projet.statut,
        "budget_initial_ht": _to_float(projet.budget_initial_ht),
        "marge_cible_pct": _to_float(projet.marge_cible_pct),
        "total_devis_ht": total_devis_ht,
        "total_cout": total_cout,
        "marge_globale_eur": marge_globale_eur,
        "taux_rendement_cout_pct": taux_rendement_cout_pct,
        "taux_marque_global": taux_marque_global,
        "can_send": total_devis_ht > 0 and taux_marque_global >= TRUTH_GATE_MIN_TAUX_MARQUE,
        "nombre_devis": len(devis_list),
        "warnings": warnings,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
