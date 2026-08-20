import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id_user = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nom = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)
    entreprise = Column(String, nullable=True)

class Projet(Base):
    __tablename__ = "projets"
    id_projet = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    id_user = Column(String, ForeignKey("users.id_user"), nullable=False)
    nom_projet = Column(String, nullable=False)
    statut = Column(String, default="EN_COURS")

class ChiffrageInverse(Base):
    __tablename__ = "chiffrage_inverse"
    id_chiffrage = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    id_projet = Column(String, ForeignKey("projets.id_projet"), nullable=False)
    prix_actuel = Column(Float, default=0.0)
    prix_cible = Column(Float, default=0.0)
    marge_actuelle_pct = Column(Float, default=0.0)
    marge_recommandee_pct = Column(Float, default=0.0)
    niveau_risque = Column(String, default="MOYEN")
    niveau_confiance = Column(String, default="MOYEN")
    version = Column(Integer, default=1)

class PassportSnapshot(Base):
    __tablename__ = "passport_snapshots"
    id_snapshot = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    id_user = Column(String, ForeignKey("users.id_user"), nullable=False)
    prix_actuel_global = Column(Float, default=0.0)
    prix_cible_global = Column(Float, default=0.0)
    ecart_global = Column(Float, default=0.0)
    marge_consolidee_pct = Column(Float, default=0.0)
    marge_recommandee_global_pct = Column(Float, default=0.0)
    trust_score_global = Column(Integer, default=100)
    risque_global = Column(String, default="FAIBLE")
    confiance_global = Column(String, default="FORT")
    nb_chantiers_actifs = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)

class ActionIA(Base):
    __tablename__ = "actions_ia"
    id_action = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    id_projet = Column(String, ForeignKey("projets.id_projet"), nullable=False)
    titre = Column(String, nullable=False)
    priorite = Column(String, default="P1_HAUTE")
    resolue = Column(Boolean, default=False)
