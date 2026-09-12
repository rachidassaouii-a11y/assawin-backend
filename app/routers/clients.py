import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.all_models import Client, Projet, Devis, User

router = APIRouter(prefix="/api/v1/clients", tags=["Clients"])


class ClientCreate(BaseModel):
    nom: str = Field(..., min_length=1)
    type_client: str = Field("particulier")
    telephone: Optional[str] = None
    email: Optional[str] = None
    adresse: Optional[str] = None
    siret: Optional[str] = None


class ClientResponse(BaseModel):
    id: str
    nom: str
    type_client: str
    telephone: Optional[str] = None
    email: Optional[str] = None
    adresse: Optional[str] = None
    siret: Optional[str] = None
    numero_client: Optional[str] = None

    class Config:
        from_attributes = True


def _generer_numero_client(db: Session, user_id: str) -> str:
    nombre_clients = (
        db.query(Client)
        .filter(Client.user_id == user_id)
        .count()
    )
    return f"CLI-{nombre_clients + 1:04d}"


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ClientResponse)
def create_client(
    data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    numero_client = _generer_numero_client(db, str(current_user.id))

    client = Client(
        id=str(uuid.uuid4()),
        user_id=str(current_user.id),
        nom=data.nom.strip(),
        type_client=data.type_client,
        telephone=data.telephone,
        email=data.email,
        adresse=data.adresse,
        siret=data.siret,
        numero_client=numero_client,
        created_at=datetime.now(timezone.utc),
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.get("/", response_model=List[ClientResponse])
def list_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Client)
        .filter(Client.user_id == str(current_user.id))
        .order_by(Client.created_at.desc())
        .all()
    )


@router.get("/{client_id}/detail")
def get_client_detail(
    client_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = (
        db.query(Client)
        .filter(Client.id == client_id, Client.user_id == str(current_user.id))
        .first()
    )
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client introuvable")

    projets = db.query(Projet).filter(Projet.client_id == client_id).all()
    projet_ids = [p.id for p in projets]
    devis_list = db.query(Devis).filter(Devis.projet_id.in_(projet_ids)).all() if projet_ids else []

    ca_total = round(sum(float(d.total_ht or 0) for d in devis_list), 2)

    return {
        "id": client.id,
        "nom": client.nom,
        "type_client": client.type_client,
        "telephone": client.telephone,
        "email": client.email,
        "adresse": client.adresse,
        "siret": client.siret,
        "numero_client": getattr(client, "numero_client", None),
        "nombre_projets": len(projets),
        "nombre_devis": len(devis_list),
        "ca_total": ca_total,
    }


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: str,
    data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = (
        db.query(Client)
        .filter(Client.id == client_id, Client.user_id == str(current_user.id))
        .first()
    )
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client introuvable")

    client.nom = data.nom.strip()
    client.type_client = data.type_client
    client.telephone = data.telephone
    client.email = data.email
    client.adresse = data.adresse
    client.siret = data.siret

    if not getattr(client, "numero_client", None):
        client.numero_client = _generer_numero_client(db, str(current_user.id))

    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}")
def delete_client(
    client_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = (
        db.query(Client)
        .filter(Client.id == client_id, Client.user_id == str(current_user.id))
        .first()
    )
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client introuvable")

    db.delete(client)
    db.commit()
    return {"message": "Client supprimé avec succès"}
