from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas
from ..auth import require_authentifie
from ..websocket import manager

router = APIRouter(prefix="/commentaires", tags=["Commentaires"])


# Ajouter un commentaire sur une intervention
@router.post("/intervention/{intervention_id}",
             response_model=schemas.CommentaireOut)
async def ajouter_commentaire(
    intervention_id: int,
    data: schemas.CommentaireCreate,
    db: Session = Depends(get_db),
    utilisateur: models.Utilisateur = Depends(require_authentifie)
):
    intervention = db.query(models.Intervention).filter(
        models.Intervention.id == intervention_id
    ).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention non trouvée")

    # Un employé ne peut commenter que ses propres signalements
    if utilisateur.role == "employe" and intervention.utilisateur_id != utilisateur.id:
        raise HTTPException(status_code=403, detail="Accès refusé")

    commentaire = models.Commentaire(
        intervention_id=intervention_id,
        auteur_id=utilisateur.id,
        contenu=data.contenu
    )
    db.add(commentaire)
    db.commit()
    db.refresh(commentaire)

    # 🔔 Notifier l'autre partie
    if utilisateur.role == "technicien":
        # Notifier l'employé
        await manager.envoyer_a(intervention.utilisateur_id, {
            "type": "nouveau_commentaire",
            "intervention_id": intervention_id,
            "auteur": utilisateur.nom,
            "contenu": data.contenu,
            "date": commentaire.date.isoformat()
        })
    else:
        # Notifier tous les techniciens
        await manager.diffuser_par_role("technicien", {
            "type": "nouveau_commentaire",
            "intervention_id": intervention_id,
            "auteur": utilisateur.nom,
            "contenu": data.contenu,
            "date": commentaire.date.isoformat()
        }, db)

    return commentaire


# Lister les commentaires d'une intervention
@router.get("/intervention/{intervention_id}",
            response_model=List[schemas.CommentaireOut])
def lister_commentaires(
    intervention_id: int,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_authentifie)
):
    return db.query(models.Commentaire).filter(
        models.Commentaire.intervention_id == intervention_id
    ).order_by(models.Commentaire.date.asc()).all()
