from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from ..database import get_db
from .. import models, schemas
from ..auth import (
    hasher_mot_de_passe, verifier_mot_de_passe,
    creer_token, ACCESS_TOKEN_EXPIRE_MINUTES,
    require_technicien
)

router = APIRouter(prefix="/auth", tags=["Authentification"])


# --------- Créer un utilisateur (réservé technicien) ---------
@router.post("/register", response_model=schemas.UtilisateurOut)
def register(
    data: schemas.UtilisateurCreate,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    # Vérifier email unique
    existe = db.query(models.Utilisateur).filter(
        models.Utilisateur.email == data.email
    ).first()
    if existe:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    utilisateur = models.Utilisateur(
        nom=data.nom,
        email=data.email,
        mot_de_passe=hasher_mot_de_passe(data.mot_de_passe),
        role=data.role or "employe",
        service_id=data.service_id,
    )
    db.add(utilisateur)
    db.commit()
    db.refresh(utilisateur)
    return utilisateur


# --------- Créer le tout premier technicien (sans auth) ---------
# À utiliser UNE SEULE FOIS au démarrage. Désactivé si un technicien existe déjà.
@router.post("/bootstrap", response_model=schemas.UtilisateurOut)
def bootstrap_technicien(
    data: schemas.UtilisateurCreate,
    db: Session = Depends(get_db)
):
    deja = db.query(models.Utilisateur).filter(
        models.Utilisateur.role == "technicien"
    ).first()
    if deja:
        raise HTTPException(status_code=403, detail="Un technicien existe déjà")

    technicien = models.Utilisateur(
        nom=data.nom,
        email=data.email,
        mot_de_passe=hasher_mot_de_passe(data.mot_de_passe),
        role="technicien",
        service_id=data.service_id,
    )
    db.add(technicien)
    db.commit()
    db.refresh(technicien)
    return technicien


# --------- Login ---------
@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    utilisateur = db.query(models.Utilisateur).filter(
        models.Utilisateur.email == form_data.username
    ).first()

    if not utilisateur or not verifier_mot_de_passe(form_data.password, utilisateur.mot_de_passe):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    if not utilisateur.actif:
        raise HTTPException(status_code=403, detail="Compte désactivé")

    token = creer_token(
        data={"sub": utilisateur.email, "role": utilisateur.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": utilisateur.role,
        "utilisateur_id": utilisateur.id,
        "nom": utilisateur.nom
    }


# --------- Profil courant ---------
@router.get("/me", response_model=schemas.UtilisateurOut)
def moi(utilisateur: models.Utilisateur = Depends(require_technicien)):
    # sera remplacé plus tard par un "require_authentifie"
    return utilisateur
