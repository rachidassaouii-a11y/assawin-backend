from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
import hashlib
import base64

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

# Base de données simulée en mémoire
fake_users_db = {}

class UserRegister(BaseModel):
    nom: str
    email: EmailStr
    password: str
    entreprise: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserRegister):
    if user.email in fake_users_db:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")
    
    hashed_password = hash_password(user.password)
    fake_users_db[user.email] = {
        "nom": user.nom,
        "email": user.email,
        "password": hashed_password,
        "entreprise": user.entreprise,
        "created_at": datetime.utcnow().isoformat()
    }
    return {
        "message": "Utilisateur créé avec succès",
        "id_user": user.email
    }

@router.post("/login")
def login(user: UserLogin):
    db_user = fake_users_db.get(user.email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email non enregistré. Veuillez d'abord exécuter /register."
        )
    
    if db_user["password"] != hash_password(user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects"
        )
    
    # Génération d'un token natif sécurisé
    token_raw = f"{user.email}:{datetime.utcnow().timestamp()}"
    access_token = base64.b64encode(token_raw.encode()).decode()
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
