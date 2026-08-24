import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
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
    id_user = Column(String, ForeignKey("users.id_user"), nullable=False, index=True)
    nom_projet = Column(String, nullable=False)
    budget_initial_ht = Column(Float, default=0.0, nullable=False)
    marge_cible_pct = Column(Float, default=30.0, nullable=False)
    statut = Column(String, default="EN_COURS", nullable=False)
    description = Column(String, nullable=True)
    date_creation = Column(DateTime, default=datetime.utcnow, nullable=False)

class Devis(Base):
    __tablename__ = "devis"
    id_devis = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    id_projet = Column(String, ForeignKey("projets.id_projet"), nullable=False, index=True)
    reference = Column(String, nullable=False)
    total_ht = Column(Float, default=0.0, nullable=False)
    cout_total = Column(Float, default=0.0, nullable=False)
    marge_cible_pct = Column(Float, default=30.0, nullable=False)
    fournisseur_non_verifie = Column(Boolean, default=False, nullable=False)
    statut = Column(String, default="BROUILLON", nullable=False)
    date_creation = Column(DateTime, default=datetime.utcnow, nullable=False)

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
