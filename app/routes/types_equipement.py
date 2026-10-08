from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas
from ..auth import require_technicien, require_authentifie

router = APIRouter(prefix="/types-equipement", tags=["Types d'équipement"])


@router.post("/", response_model=schemas.TypeEquipementOut)
def creer_type(
    data: schemas.TypeEquipementCreate,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    existe = db.query(models.TypeEquipement).filter(
        models.TypeEquipement.nom == data.nom
    ).first()
    if existe:
        raise HTTPException(status_code=400, detail="Type déjà existant")
    type_eq = models.TypeEquipement(nom=data.nom)
    db.add(type_eq)
    db.commit()
    db.refresh(type_eq)
    return type_eq


@router.get("/", response_model=List[schemas.TypeEquipementOut])
def lister_types(
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_authentifie)
):
    return db.query(models.TypeEquipement).all()


@router.delete("/{type_id}")
def supprimer_type(
    type_id: int,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    type_eq = db.query(models.TypeEquipement).filter(
        models.TypeEquipement.id == type_id
    ).first()
    if not type_eq:
        raise HTTPException(status_code=404, detail="Type non trouvé")

    # Vérifier si des équipements utilisent ce type
    nb_equipements = db.query(models.Equipement).filter(
        models.Equipement.type_id == type_id
    ).count()

    if nb_equipements > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de supprimer : {nb_equipements} équipement(s) utilisent ce type. Modifiez-les ou supprimez-les d'abord."
        )

    db.delete(type_eq)
    db.commit()
    return {"message": "Type supprimé"}
