from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.all_models import User

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

class UserRegister(BaseModel):
    nom: str
    email: EmailStr
    password: str
    entreprise: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    user = User(
        nom=user_in.nom,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        entreprise=user_in.entreprise
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Utilisateur créé", "id_user": user.id_user}

@router.post("/login")
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    
    token = create_access_token({"sub": user.id_user})
    return {"access_token": token, "token_type": "bearer"}
