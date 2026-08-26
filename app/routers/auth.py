from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from jose import jwt
from passlib.context import CryptContext

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

SECRET_KEY = "assawin_secret_key_change_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserRegister):
    if user.email in fake_users_db:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")
    
    hashed_password = pwd_context.hash(user.password)
    fake_users_db[user.email] = {
        "nom": user.nom,
        "email": user.email,
        "password": hashed_password,
        "entreprise": user.entreprise,
        "created_at": datetime.utcnow().isoformat()
    }
    return {
        "message": "Utilisateur créé",
        "id_user": user.email
    }

@router.post("/login")
def login(user: UserLogin):
    try:
        db_user = fake_users_db.get(user.email)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email non enregistré. Veuillez d'abord exécuter /register."
            )
        
        if not pwd_context.verify(user.password, db_user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Identifiants incorrects"
            )
        
        expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"sub": user.email, "exp": datetime.utcnow() + expire}
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return {
            "access_token": encoded_jwt,
            "token_type": "bearer"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne: {str(e)}"
        )
