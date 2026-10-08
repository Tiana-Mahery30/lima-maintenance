from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas
from ..auth import require_technicien, require_authentifie

router = APIRouter(prefix="/parametres", tags=["Paramètres"])


@router.get("/", response_model=List[schemas.ParametreOut])
def lister_parametres(
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    return db.query(models.Parametre).all()


@router.get("/{cle}")
def obtenir_parametre(
    cle: str,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_authentifie)
):
    parametre = db.query(models.Parametre).filter(
        models.Parametre.cle == cle
    ).first()
    if not parametre:
        raise HTTPException(status_code=404, detail="Paramètre non trouvé")
    return {"cle": parametre.cle, "valeur": parametre.valeur}


@router.put("/{cle}", response_model=schemas.ParametreOut)
def modifier_parametre(
    cle: str,
    data: schemas.ParametreBase,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    parametre = db.query(models.Parametre).filter(
        models.Parametre.cle == cle
    ).first()
    if not parametre:
        parametre = models.Parametre(cle=cle, valeur=data.valeur)
        db.add(parametre)
    else:
        parametre.valeur = data.valeur
    db.commit()
    db.refresh(parametre)
    return parametre


@router.post("/", response_model=schemas.ParametreOut)
def creer_parametre(
    data: schemas.ParametreCreate,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    existe = db.query(models.Parametre).filter(
        models.Parametre.cle == data.cle
    ).first()
    if existe:
        raise HTTPException(status_code=400, detail="Paramètre déjà existant")
    parametre = models.Parametre(**data.dict())
    db.add(parametre)
    db.commit()
    db.refresh(parametre)
    return parametre


@router.delete("/{cle}")
def supprimer_parametre(
    cle: str,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    parametre = db.query(models.Parametre).filter(
        models.Parametre.cle == cle
    ).first()
    if not parametre:
        raise HTTPException(status_code=404, detail="Paramètre non trouvé")
    db.delete(parametre)
    db.commit()
    return {"message": "Paramètre supprimé"}
