import os
import shutil
import uuid
from fastapi import (
    APIRouter, Depends, HTTPException, UploadFile, File, Form
)
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from .. import models, schemas
from ..auth import require_technicien, require_authentifie, get_utilisateur_courant
from ..websocket import manager

router = APIRouter(prefix="/interventions", tags=["Interventions"])

UPLOAD_DIR = "static/uploads/interventions"
os.makedirs(UPLOAD_DIR, exist_ok=True)

EXTENSIONS_AUTORISEES = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def sauvegarder_photo(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in EXTENSIONS_AUTORISEES:
        raise HTTPException(status_code=400, detail=f"Extension non autorisée : {ext}")
    nom_unique = f"{uuid.uuid4().hex}{ext}"
    chemin = os.path.join(UPLOAD_DIR, nom_unique)
    with open(chemin, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return f"/{chemin}"


async def creer_notification(db: Session, utilisateur_id: int, message: str, type_: str):
    notif = models.Notification(
        utilisateur_id=utilisateur_id,
        message=message,
        type=type_
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    # Envoi temps réel via WebSocket
    await manager.envoyer_a(utilisateur_id, {
        "type": "notification",
        "id": notif.id,
        "message": message,
        "type_notif": type_,
        "date": notif.date.isoformat()
    })
    return notif


# ---------- Créer une intervention (signalement employé) ----------
@router.post("/", response_model=schemas.InterventionOut)
async def creer_intervention(
    equipement_id: int = Form(...),
    description_panne: str = Form(...),
    priorite_id: Optional[int] = Form(None),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    utilisateur: models.Utilisateur = Depends(require_authentifie)
):
    equipement = db.query(models.Equipement).filter(
        models.Equipement.id == equipement_id
    ).first()
    if not equipement:
        raise HTTPException(status_code=404, detail="Equipement non trouvé")

    photo_path = None
    if photo and photo.filename:
        photo_path = sauvegarder_photo(photo)

    intervention = models.Intervention(
        utilisateur_id=utilisateur.id,
        equipement_id=equipement_id,
        priorite_id=priorite_id,
        description_panne=description_panne,
        photo_panne=photo_path,
        statut="en_attente"
    )
    db.add(intervention)
    db.commit()
    db.refresh(intervention)

    # 🔔 Notification temps réel à tous les techniciens
    await manager.diffuser_par_role("technicien", {
        "type": "nouvelle_intervention",
        "intervention_id": intervention.id,
        "message": f"Nouveau signalement : {equipement.marque} {equipement.modele or ''} par {utilisateur.nom}",
        "priorite_id": priorite_id,
        "date": intervention.date_signalement.isoformat()
    }, db)

    return intervention


# ---------- Lister les interventions ----------
@router.get("/", response_model=List[schemas.InterventionOut])
def lister_interventions(
    statut: Optional[str] = None,
    equipement_id: Optional[int] = None,
    utilisateur_id: Optional[int] = None,
    mes_signalements: Optional[bool] = False,
    db: Session = Depends(get_db),
    utilisateur: models.Utilisateur = Depends(require_authentifie)
):
    query = db.query(models.Intervention).filter(
        models.Intervention.archive == False
    )

    # Un employé ne voit que ses propres signalements
    if utilisateur.role == "employe" or mes_signalements:
        query = query.filter(models.Intervention.utilisateur_id == utilisateur.id)
    elif utilisateur_id:
        query = query.filter(models.Intervention.utilisateur_id == utilisateur_id)

    if statut:
        query = query.filter(models.Intervention.statut == statut)
    if equipement_id:
        query = query.filter(models.Intervention.equipement_id == equipement_id)

    return query.order_by(models.Intervention.date_signalement.desc()).all()


# ---------- Obtenir une intervention ----------
@router.get("/{intervention_id}", response_model=schemas.InterventionOut)
def obtenir_intervention(
    intervention_id: int,
    db: Session = Depends(get_db),
    utilisateur: models.Utilisateur = Depends(require_authentifie)
):
    intervention = db.query(models.Intervention).filter(
        models.Intervention.id == intervention_id
    ).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention non trouvée")

    # Un employé ne peut voir que les siennes
    if utilisateur.role == "employe" and intervention.utilisateur_id != utilisateur.id:
        raise HTTPException(status_code=403, detail="Accès refusé")

    return intervention


# ---------- Prendre en charge une intervention (technicien) ----------
@router.put("/{intervention_id}/prendre-en-charge", response_model=schemas.InterventionOut)
async def prendre_en_charge(
    intervention_id: int,
    db: Session = Depends(get_db),
    technicien: models.Utilisateur = Depends(require_technicien)
):
    intervention = db.query(models.Intervention).filter(
        models.Intervention.id == intervention_id
    ).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention non trouvée")

    if intervention.statut != "en_attente":
        raise HTTPException(status_code=400, detail="Intervention déjà prise en charge")

    intervention.statut = "en_cours"
    intervention.date_prise_en_charge = datetime.utcnow()
    intervention.equipement.etat = "en panne"
    db.commit()
    db.refresh(intervention)

    # 🔔 Notifier l'employé concerné
    await creer_notification(
        db,
        intervention.utilisateur_id,
        f"Votre signalement #{intervention.id} est pris en charge",
        "prise_en_charge"
    )

    return intervention


# ---------- Clôturer une intervention (technicien) ----------
@router.put("/{intervention_id}/cloturer", response_model=schemas.InterventionOut)
async def cloturer_intervention(
    intervention_id: int,
    actions_realisees: str = Form(...),
    resultat: str = Form(...),
    db: Session = Depends(get_db),
    technicien: models.Utilisateur = Depends(require_technicien)
):
    intervention = db.query(models.Intervention).filter(
        models.Intervention.id == intervention_id
    ).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention non trouvée")

    if intervention.statut == "terminee":
        raise HTTPException(status_code=400, detail="Intervention déjà clôturée")

    intervention.statut = "terminee"
    intervention.actions_realisees = actions_realisees
    intervention.resultat = resultat
    intervention.date_fin = datetime.utcnow()
    intervention.equipement.etat = "fonctionnel"
    db.commit()
    db.refresh(intervention)

    # 🔔 Notifier l'employé concerné
    await creer_notification(
        db,
        intervention.utilisateur_id,
        f"Votre signalement #{intervention.id} est résolu",
        "cloture"
    )

    return intervention


# ---------- Réouvrir une intervention (technicien) ----------
@router.put("/{intervention_id}/reouvrir", response_model=schemas.InterventionOut)
async def reouvrir_intervention(
    intervention_id: int,
    db: Session = Depends(get_db),
    technicien: models.Utilisateur = Depends(require_technicien)
):
    intervention = db.query(models.Intervention).filter(
        models.Intervention.id == intervention_id
    ).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention non trouvée")

    intervention.statut = "en_cours"
    intervention.date_fin = None
    intervention.equipement.etat = "en panne"
    db.commit()
    db.refresh(intervention)

    await creer_notification(
        db,
        intervention.utilisateur_id,
        f"Votre signalement #{intervention.id} a été réouvert",
        "reouverture"
    )
    return intervention


# ---------- Historique des interventions d'un équipement ----------
@router.get("/equipement/{equipement_id}/historique",
            response_model=List[schemas.InterventionOut])
def historique_equipement(
    equipement_id: int,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_authentifie)
):
    return db.query(models.Intervention).filter(
        models.Intervention.equipement_id == equipement_id
    ).order_by(models.Intervention.date_signalement.desc()).all()


# ---------- Annuler une intervention (employé propriétaire, en attente uniquement) ----------
@router.put("/{intervention_id}/annuler", response_model=schemas.InterventionOut)
async def annuler_intervention(
    intervention_id: int,
    db: Session = Depends(get_db),
    utilisateur: models.Utilisateur = Depends(require_authentifie)
):
    intervention = db.query(models.Intervention).filter(
        models.Intervention.id == intervention_id
    ).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention non trouvée")

    # Vérifier que c'est bien le propriétaire
    if intervention.utilisateur_id != utilisateur.id:
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez annuler que vos propres signalements"
        )

    # Vérifier que le statut est "en_attente"
    if intervention.statut != "en_attente":
        raise HTTPException(
            status_code=400,
            detail="Impossible d'annuler un signalement déjà pris en charge ou terminé"
        )

    # Vérifier qu'il n'est pas déjà archivé
    if intervention.archive:
        raise HTTPException(status_code=400, detail="Ce signalement est déjà annulé")

    # Archiver
    intervention.archive = True
    db.commit()
    db.refresh(intervention)

    # 🔔 Notifier tous les techniciens
    await manager.diffuser_par_role("technicien", {
        "type": "intervention_annulee",
        "intervention_id": intervention.id,
        "message": f"Signalement #{intervention.id} annulé par {utilisateur.nom}",
        "date": datetime.utcnow().isoformat()
    }, db)

    return intervention


# ---------- Archiver une intervention (soft delete, technicien) ----------
@router.delete("/{intervention_id}")
def archiver_intervention(
    intervention_id: int,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    intervention = db.query(models.Intervention).filter(
        models.Intervention.id == intervention_id
    ).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention non trouvée")

    intervention.archive = True
    db.commit()
    return {"message": "Intervention archivée"}
