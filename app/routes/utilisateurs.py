from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas
from ..auth import require_technicien, require_authentifie, get_utilisateur_courant

router = APIRouter(prefix="/utilisateurs", tags=["Utilisateurs"])


# Lister tous les utilisateurs (technicien)
@router.get("/", response_model=List[schemas.UtilisateurOut])
def lister_utilisateurs(
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    return db.query(models.Utilisateur).filter(
        models.Utilisateur.actif == True
    ).all()


# Obtenir un utilisateur par ID
@router.get("/{utilisateur_id}", response_model=schemas.UtilisateurOut)
def obtenir_utilisateur(
    utilisateur_id: int,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_authentifie)
):
    utilisateur = db.query(models.Utilisateur).filter(
        models.Utilisateur.id == utilisateur_id
    ).first()
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return utilisateur


# Modifier un utilisateur (technicien)
@router.put("/{utilisateur_id}", response_model=schemas.UtilisateurOut)
def modifier_utilisateur(
    utilisateur_id: int,
    data: schemas.UtilisateurUpdate,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    utilisateur = db.query(models.Utilisateur).filter(
        models.Utilisateur.id == utilisateur_id
    ).first()
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(utilisateur, key, value)

    db.commit()
    db.refresh(utilisateur)
    return utilisateur


# Désactiver un utilisateur (soft delete)
@router.delete("/{utilisateur_id}")
def desactiver_utilisateur(
    utilisateur_id: int,
    db: Session = Depends(get_db),
    technicien: models.Utilisateur = Depends(require_technicien)
):
    if utilisateur_id == technicien.id:
        raise HTTPException(status_code=400, detail="Impossible de se désactiver soi-même")

    utilisateur = db.query(models.Utilisateur).filter(
        models.Utilisateur.id == utilisateur_id
    ).first()
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    utilisateur.actif = False
    db.commit()
    return {"message": "Utilisateur désactivé"}


# Mes équipements affectés (employé connecté)
@router.get("/me/equipements", response_model=List[schemas.AffectationOut])
def mes_equipements(
    db: Session = Depends(get_db),
    utilisateur: models.Utilisateur = Depends(require_authentifie)
):
    return db.query(models.Affectation).filter(
        models.Affectation.utilisateur_id == utilisateur.id,
        models.Affectation.actif == True
    ).all()
