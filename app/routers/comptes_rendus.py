import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.all_models import CompteRendu, Projet, User

router = APIRouter(prefix="/api/v1/comptes-rendus", tags=["Comptes-rendus"])


class CompteRenduCreate(BaseModel):
    projet_id: str
    titre: str = Field(..., min_length=1)
    contenu: Optional[str] = None


class CompteRenduResponse(BaseModel):
    id: str
    projet_id: str
    titre: str
    contenu: Optional[str] = None

    class Config:
        from_attributes = True


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CompteRenduResponse)
def creer_compte_rendu(
    data: CompteRenduCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    projet = (
        db.query(Projet)
        .filter(Projet.id == data.projet_id, Projet.user_id == str(current_user.id))
        .first()
    )
    if not projet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable ou non autorisé")

    cr = CompteRendu(
        id=str(uuid.uuid4()),
        projet_id=data.projet_id,
        titre=data.titre.strip(),
        contenu=data.contenu,
        created_at=datetime.now(timezone.utc),
    )
    db.add(cr)
    db.commit()
    db.refresh(cr)
    return cr


@router.get("/projet/{projet_id}", response_model=List[CompteRenduResponse])
def lister_comptes_rendus_projet(
    projet_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    projet = (
        db.query(Projet)
        .filter(Projet.id == projet_id, Projet.user_id == str(current_user.id))
        .first()
    )
    if not projet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable ou non autorisé")

    return db.query(CompteRendu).filter(CompteRendu.projet_id == projet_id).order_by(CompteRendu.created_at.desc()).all()


@router.delete("/{cr_id}")
def supprimer_compte_rendu(
    cr_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cr = (
        db.query(CompteRendu)
        .join(Projet, CompteRendu.projet_id == Projet.id)
        .filter(CompteRendu.id == cr_id, Projet.user_id == str(current_user.id))
        .first()
    )
    if not cr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compte-rendu introuvable ou non autorisé")

    db.delete(cr)
    db.commit()
    return {"message": "Compte-rendu supprimé avec succès"}
