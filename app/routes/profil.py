from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from .. import models
from ..auth import require_authentifie, hasher_mot_de_passe, verifier_mot_de_passe

router = APIRouter(prefix="/profil", tags=["Profil"])


class ChangerMotDePasse(BaseModel):
    ancien_mot_de_passe: str
    nouveau_mot_de_passe: str


@router.get("/me")
def mon_profil(
    utilisateur: models.Utilisateur = Depends(require_authentifie)
):
    return {
        "id": utilisateur.id,
        "nom": utilisateur.nom,
        "email": utilisateur.email,
        "role": utilisateur.role,
        "service_id": utilisateur.service_id,
        "date_creation": utilisateur.date_creation,
    }


@router.put("/changer-mot-de-passe")
def changer_mot_de_passe(
    data: ChangerMotDePasse,
    db: Session = Depends(get_db),
    utilisateur: models.Utilisateur = Depends(require_authentifie)
):
    if not verifier_mot_de_passe(data.ancien_mot_de_passe, utilisateur.mot_de_passe):
        raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect")

    if len(data.nouveau_mot_de_passe) < 6:
        raise HTTPException(status_code=400, detail="Le nouveau mot de passe doit faire au moins 6 caractères")

    if data.ancien_mot_de_passe == data.nouveau_mot_de_passe:
        raise HTTPException(status_code=400, detail="Le nouveau mot de passe doit être différent de l'ancien")

    utilisateur.mot_de_passe = hasher_mot_de_passe(data.nouveau_mot_de_passe)
    db.commit()

    return {"message": "Mot de passe modifié avec succès"}
