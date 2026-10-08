from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .database import get_db
from . import models


SECRET_KEY = "CHANGE_MOI_EN_PRODUCTION_LIMA_2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8   # 8 heures


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ---------- Hash / Vérification ----------
def hasher_mot_de_passe(mot_de_passe: str) -> str:
    return pwd_context.hash(mot_de_passe)


def verifier_mot_de_passe(mot_de_passe: str, hash: str) -> bool:
    return pwd_context.verify(mot_de_passe, hash)


# ---------- Création du token JWT ----------
def creer_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ---------- Récupérer l'utilisateur courant ----------
def get_utilisateur_courant(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.Utilisateur:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    utilisateur = db.query(models.Utilisateur).filter(
        models.Utilisateur.email == email
    ).first()
    if utilisateur is None or not utilisateur.actif:
        raise credentials_exception
    return utilisateur


# ---------- Vérifier le rôle technicien ----------
def require_technicien(
    utilisateur: models.Utilisateur = Depends(get_utilisateur_courant)
) -> models.Utilisateur:
    if utilisateur.role != "technicien":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé au technicien"
        )
    return utilisateur


# ---------- Vérifier employé ou technicien ----------
def require_authentifie(
    utilisateur: models.Utilisateur = Depends(get_utilisateur_courant)
) -> models.Utilisateur:
    return utilisateur
