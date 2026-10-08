from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from .. import models, schemas
from ..auth import require_technicien, require_authentifie

router = APIRouter(prefix="/affectations", tags=["Affectations"])


# Attribuer un équipement à un employé
@router.post("/", response_model=schemas.AffectationOut)
def creer_affectation(
    data: schemas.AffectationCreate,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    equipement = db.query(models.Equipement).filter(
        models.Equipement.id == data.equipement_id
    ).first()
    if not equipement:
        raise HTTPException(status_code=404, detail="Equipement non trouvé")

    utilisateur = db.query(models.Utilisateur).filter(
        models.Utilisateur.id == data.utilisateur_id
    ).first()
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Vérifier qu'il n'y a pas déjà une affectation active
    affectation_active = db.query(models.Affectation).filter(
        models.Affectation.equipement_id == data.equipement_id,
        models.Affectation.actif == True
    ).first()
    if affectation_active:
        raise HTTPException(
            status_code=400,
            detail="Cet équipement est déjà attribué à quelqu'un"
        )

    affectation = models.Affectation(
        equipement_id=data.equipement_id,
        utilisateur_id=data.utilisateur_id,
    )
    equipement.statut = "occupé"
    db.add(affectation)
    db.commit()
    db.refresh(affectation)
    return affectation


# Lister toutes les affectations actives
@router.get("/", response_model=List[schemas.AffectationOut])
def lister_affectations(
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    return db.query(models.Affectation).filter(
        models.Affectation.actif == True
    ).all()


# Terminer une affectation (retour de l'équipement)
@router.put("/{affectation_id}/terminer", response_model=schemas.AffectationOut)
def terminer_affectation(
    affectation_id: int,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    affectation = db.query(models.Affectation).filter(
        models.Affectation.id == affectation_id
    ).first()
    if not affectation:
        raise HTTPException(status_code=404, detail="Affectation non trouvée")
    if not affectation.actif:
        raise HTTPException(status_code=400, detail="Affectation déjà terminée")

    affectation.actif = False
    affectation.date_fin = datetime.utcnow()

    equipement = affectation.equipement
    equipement.statut = "disponible"

    db.commit()
    db.refresh(affectation)
    return affectation


# Historique des affectations d'un équipement
@router.get("/equipement/{equipement_id}", response_model=List[schemas.AffectationOut])
def historique_affectations(
    equipement_id: int,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    return db.query(models.Affectation).filter(
        models.Affectation.equipement_id == equipement_id
    ).order_by(models.Affectation.date_debut.desc()).all()
