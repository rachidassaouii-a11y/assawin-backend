Oui. Vu ce que tu indiques — python-jose est déjà installé dans requirements.txt — je recommande clairement l'Option 1.

C'est la correction la plus rapide et la plus propre : ne pas ajouter une deuxième bibliothèque JWT alors que python-jose est déjà présente.

Dans app/core/security.py

Remplace uniquement :

import jwt

par :

from jose import jwt

Ton fichier devient :

from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.all_models import User


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(days=1)

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm="HS256"
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Token invalide"
            )

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Token expiré ou invalide"
        )

    user = (
        db.query(User)
        .filter(User.id_user == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Utilisateur introuvable"
        )

    return user

Action immédiate

1. Ouvre app/core/security.py.


2. Remplace import jwt par from jose import jwt.


3. Enregistre.


4. Commit et push sur GitHub.


5. Render redéploiera automatiquement.



Ne modifie pas auth.py, main.py ni les routeurs pour cette erreur précise. Le crash actuel est bien déclenché dès l'import de security.py, avant même le démarrage de FastAPI.

Si python-jose est effectivement déjà dans ton requirements.txt, cette correction doit supprimer précisément le :

ModuleNotFoundError: No module named 'jwt'

Après le redéploiement, la première vérification est /health, puis /docs.