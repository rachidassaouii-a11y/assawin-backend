import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


# =====================================================
# USER
# =====================================================

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nom = Column(String)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    projets = relationship("Projet", back_populates="user")


# =====================================================
# CLIENT
# =====================================================

class Client(Base):
    __tablename__ = "clients"

    id = Column(String(36), primary_key=True, default=generate_uuid)

    user_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False
    )

    nom = Column(String, nullable=False)

    type_client = Column(
        String,
        default="particulier"
    )

    telephone = Column(String)
    email = Column(String)
    adresse = Column(String)
    siret = Column(String)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    projets = relationship(
        "Projet",
        back_populates="client"
    )


# =====================================================
# PROJET
# =====================================================

class Projet(Base):
    __tablename__ = "projets"

    id = Column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )

    nom_projet = Column(
        String,
        nullable=False
    )

    budget_initial_ht = Column(
        Float,
        default=0.0
    )

    user_id = Column(
        String(36),
        ForeignKey("users.id")
    )

    client_id = Column(
        String(36),
        ForeignKey("clients.id"),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    user = relationship(
        "User",
        back_populates="projets"
    )

    client = relationship(
        "Client",
        back_populates="projets"
    )

    devis = relationship(
        "Devis",
        back_populates="projet"
    )

    photos = relationship(
        "Photo",
        back_populates="projet"
    )

    comptes_rendus = relationship(
        "CompteRendu",
        back_populates="projet"
    )

    alertes = relationship(
        "Alerte",
        back_populates="projet"
    )

    decisions = relationship(
        "Decision",
        back_populates="projet"
    )

    avancements = relationship(
        "Avancement",
        back_populates="projet"
    )


# =====================================================
# DEVIS
# =====================================================

class Devis(Base):
    __tablename__ = "devis"

    id = Column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )

    total_ht = Column(
        Float,
        default=0.0
    )

    cout_total = Column(
        Float,
        default=0.0
    )
    marge_cible_pct = Column(
    Float,
    default=30.0
)

statut = Column(
    String,
    default="EN_COURS"
)

description = Column(
    String,
    nullable=True
)

adresse = Column(
    String,
    nullable=True
)

    projet_id = Column(
        String(36),
        ForeignKey("projets.id")
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    projet = relationship(
        "Projet",
        back_populates="devis"
    )


# =====================================================
# ALERTE
# =====================================================

class Alerte(Base):
    __tablename__ = "alertes"

    id = Column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )

    niveau = Column(
        String,
        default="info"
    )

    message = Column(String)

    projet_id = Column(
        String(36),
        ForeignKey("projets.id")
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    projet = relationship(
        "Projet",
        back_populates="alertes"
    )


# =====================================================
# DECISION
# =====================================================

class Decision(Base):
    __tablename__ = "decisions"

    id = Column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )

    action = Column(String)

    date = Column(Date)

    projet_id = Column(
        String(36),
        ForeignKey("projets.id")
    )

    projet = relationship(
        "Projet",
        back_populates="decisions"
    )


# =====================================================
# AVANCEMENT
# =====================================================

class Avancement(Base):
    __tablename__ = "avancement"

    id = Column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )

    pourcentage = Column(
        Float,
        default=0.0
    )

    projet_id = Column(
        String(36),
        ForeignKey("projets.id")
    )

    projet = relationship(
        "Projet",
        back_populates="avancements"
    )


# =====================================================
# PHOTO
# =====================================================

class Photo(Base):
    __tablename__ = "photos"

    id = Column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )

    projet_id = Column(
        String(36),
        ForeignKey("projets.id")
    )

    image_base64 = Column(
        String,
        nullable=False
    )

    legende = Column(String)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    projet = relationship(
        "Projet",
        back_populates="photos"
    )


# =====================================================
# COMPTE RENDU
# =====================================================

class CompteRendu(Base):
    __tablename__ = "comptes_rendus"

    id = Column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )

    projet_id = Column(
        String(36),
        ForeignKey("projets.id")
    )

    titre = Column(
        String,
        nullable=False
    )

    contenu = Column(String)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    projet = relationship(
        "Projet",
        back_populates="comptes_rendus"
    )


# =====================================================
# NOTIFICATION
# =====================================================

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )

    user_id = Column(
        String(36),
        ForeignKey("users.id")
    )

    message = Column(
        String,
        nullable=False
    )

    lu = Column(
        String,
        default="non"
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
