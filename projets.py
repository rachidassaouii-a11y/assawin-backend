import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nom = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    projets = relationship("Projet", back_populates="user")

class Projet(Base):
    __tablename__ = "projets"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    nom_projet = Column(String, nullable=False)
    budget_initial_ht = Column(Float, default=0.0)
    user_id = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="projets")
    devis = relationship("Devis", back_populates="projet")
    alertes = relationship("Alerte", back_populates="projet")
    decisions = relationship("Decision", back_populates="projet")
    avancements = relationship("Avancement", back_populates="projet")

class Devis(Base):
    __tablename__ = "devis"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    total_ht = Column(Float, default=0.0)
    cout_total = Column(Float, default=0.0)
    projet_id = Column(String(36), ForeignKey("projets.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    projet = relationship("Projet", back_populates="devis")

class Alerte(Base):
    __tablename__ = "alertes"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    niveau = Column(String, default="info")
    message = Column(String)
    projet_id = Column(String(36), ForeignKey("projets.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    projet = relationship("Projet", back_populates="alertes")

class Decision(Base):
    __tablename__ = "decisions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    action = Column(String)
    date = Column(Date)
    projet_id = Column(String(36), ForeignKey("projets.id"))
    
    projet = relationship("Projet", back_populates="decisions")

class Avancement(Base):
    __tablename__ = "avancement"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    pourcentage = Column(Float, default=0.0)
    projet_id = Column(String(36), ForeignKey("projets.id"))
    
    projet = relationship("Projet", back_populates="avancements")
