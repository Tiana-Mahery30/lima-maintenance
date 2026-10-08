from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas
from ..auth import require_technicien, require_authentifie

router = APIRouter(prefix="/services", tags=["Services"])


@router.post("/", response_model=schemas.ServiceOut)
def creer_service(
    data: schemas.ServiceCreate,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    existe = db.query(models.Service).filter(models.Service.nom == data.nom).first()
    if existe:
        raise HTTPException(status_code=400, detail="Service déjà existant")
    service = models.Service(nom=data.nom)
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.get("/", response_model=List[schemas.ServiceOut])
def lister_services(
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_authentifie)
):
    return db.query(models.Service).all()


@router.delete("/{service_id}")
def supprimer_service(
    service_id: int,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service non trouvé")

    # Vérifier si des utilisateurs sont dans ce service
    nb_users = db.query(models.Utilisateur).filter(
        models.Utilisateur.service_id == service_id
    ).count()

    if nb_users > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de supprimer : {nb_users} utilisateur(s) sont dans ce service. Réaffectez-les d'abord."
        )

    db.delete(service)
    db.commit()
    return {"message": "Service supprimé"}
