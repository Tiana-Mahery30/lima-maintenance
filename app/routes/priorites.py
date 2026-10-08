from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas
from ..auth import require_technicien, require_authentifie

router = APIRouter(prefix="/priorites", tags=["Priorités"])


@router.post("/", response_model=schemas.PrioriteOut)
def creer_priorite(
    data: schemas.PrioriteCreate,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    existe = db.query(models.Priorite).filter(
        models.Priorite.nom == data.nom
    ).first()
    if existe:
        raise HTTPException(status_code=400, detail="Priorité déjà existante")
    priorite = models.Priorite(**data.dict())
    db.add(priorite)
    db.commit()
    db.refresh(priorite)
    return priorite


@router.get("/", response_model=List[schemas.PrioriteOut])
def lister_priorites(
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_authentifie)
):
    return db.query(models.Priorite).order_by(models.Priorite.ordre).all()


@router.delete("/{priorite_id}")
def supprimer_priorite(
    priorite_id: int,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    priorite = db.query(models.Priorite).filter(
        models.Priorite.id == priorite_id
    ).first()
    if not priorite:
        raise HTTPException(status_code=404, detail="Priorité non trouvée")
    db.delete(priorite)
    db.commit()
    return {"message": "Priorité supprimée"}
