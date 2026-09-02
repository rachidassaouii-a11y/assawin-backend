import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.all_models import Photo, Projet, User

router = APIRouter(prefix="/api/v1/photos", tags=["Photos"])


class PhotoCreate(BaseModel):
    projet_id: str
    image_base64: str = Field(..., min_length=1)
    legende: str | None = None


class PhotoResponse(BaseModel):
    id: str
    projet_id: str
    image_base64: str
    legende: str | None = None

    class Config:
        from_attributes = True


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PhotoResponse)
def upload_photo(
    data: PhotoCreate,
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

    photo = Photo(
        id=str(uuid.uuid4()),
        projet_id=data.projet_id,
        image_base64=data.image_base64,
        legende=data.legende,
        created_at=datetime.now(timezone.utc),
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


@router.get("/projet/{projet_id}", response_model=List[PhotoResponse])
def lister_photos_projet(
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

    return db.query(Photo).filter(Photo.projet_id == projet_id).order_by(Photo.created_at.desc()).all()


@router.delete("/{photo_id}")
def supprimer_photo(
    photo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    photo = (
        db.query(Photo)
        .join(Projet, Photo.projet_id == Projet.id)
        .filter(Photo.id == photo_id, Projet.user_id == str(current_user.id))
        .first()
    )
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo introuvable ou non autorisée")

    db.delete(photo)
    db.commit()
    return {"message": "Photo supprimée avec succès"}
