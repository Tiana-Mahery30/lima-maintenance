import os
import shutil
import uuid
from fastapi import (
    APIRouter, Depends, HTTPException, UploadFile, File, Form
)
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..database import get_db
from .. import models, schemas
from ..auth import require_technicien, require_authentifie

router = APIRouter(prefix="/equipements", tags=["Equipements"])

UPLOAD_DIR = "static/uploads/equipements"
os.makedirs(UPLOAD_DIR, exist_ok=True)

EXTENSIONS_AUTORISEES = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def sauvegarder_image(file: UploadFile) -> str:
    """Sauvegarde un fichier image et retourne son chemin relatif."""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in EXTENSIONS_AUTORISEES:
        raise HTTPException(
            status_code=400,
            detail=f"Extension non autorisée : {ext}"
        )
    nom_unique = f"{uuid.uuid4().hex}{ext}"
    chemin = os.path.join(UPLOAD_DIR, nom_unique)
    with open(chemin, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return f"/{chemin}"


# --------- Créer un équipement (avec images optionnelles) ---------
@router.post("/", response_model=schemas.EquipementOut)
def creer_equipement(
    type_id: int = Form(...),
    marque: str = Form(...),
    modele: Optional[str] = Form(None),
    numero_serie: str = Form(...),
    statut: str = Form("disponible"),
    etat: str = Form("fonctionnel"),
    date_acquisition: Optional[str] = Form(None),
    images: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    # Vérifier numéro de série unique
    existe = db.query(models.Equipement).filter(
        models.Equipement.numero_serie == numero_serie
    ).first()
    if existe:
        raise HTTPException(status_code=400, detail="Numéro de série déjà utilisé")

    # Vérifier le type
    type_eq = db.query(models.TypeEquipement).filter(
        models.TypeEquipement.id == type_id
    ).first()
    if not type_eq:
        raise HTTPException(status_code=404, detail="Type d'équipement non trouvé")

    # Convertir la date si fournie
    date_acq = None
    if date_acquisition:
        try:
            from datetime import datetime
            date_acq = datetime.strptime(date_acquisition, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date invalide (YYYY-MM-DD)")

    equipement = models.Equipement(
        type_id=type_id,
        marque=marque,
        modele=modele,
        numero_serie=numero_serie,
        statut=statut,
        etat=etat,
        date_acquisition=date_acq,
    )
    db.add(equipement)
    db.commit()
    db.refresh(equipement)

    # Sauvegarder les images
    for img in images:
        if img.filename:
            chemin = sauvegarder_image(img)
            db.add(models.ImageEquipement(
                equipement_id=equipement.id,
                chemin=chemin
            ))
    db.commit()
    db.refresh(equipement)
    return equipement


# --------- Lister tous les équipements ---------
@router.get("/", response_model=List[schemas.EquipementOut])
def lister_equipements(
    type_id: Optional[int] = None,
    statut: Optional[str] = None,
    etat: Optional[str] = None,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_authentifie)
):
    query = db.query(models.Equipement).filter(models.Equipement.actif == True)
    if type_id:
        query = query.filter(models.Equipement.type_id == type_id)
    if statut:
        query = query.filter(models.Equipement.statut == statut)
    if etat:
        query = query.filter(models.Equipement.etat == etat)
    return query.all()


# --------- Obtenir un équipement ---------
@router.get("/{equipement_id}", response_model=schemas.EquipementOut)
def obtenir_equipement(
    equipement_id: int,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_authentifie)
):
    equipement = db.query(models.Equipement).filter(
        models.Equipement.id == equipement_id
    ).first()
    if not equipement:
        raise HTTPException(status_code=404, detail="Equipement non trouvé")
    return equipement


# --------- Modifier un équipement ---------
@router.put("/{equipement_id}", response_model=schemas.EquipementOut)
def modifier_equipement(
    equipement_id: int,
    data: schemas.EquipementUpdate,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    equipement = db.query(models.Equipement).filter(
        models.Equipement.id == equipement_id
    ).first()
    if not equipement:
        raise HTTPException(status_code=404, detail="Equipement non trouvé")

    # Vérifier unicité du numéro de série s'il est modifié
    if data.numero_serie and data.numero_serie != equipement.numero_serie:
        existe = db.query(models.Equipement).filter(
            models.Equipement.numero_serie == data.numero_serie,
            models.Equipement.id != equipement_id
        ).first()
        if existe:
            raise HTTPException(status_code=400, detail="Ce numéro de série est déjà utilisé")

    # Vérifier que le type existe s'il est modifié
    if data.type_id is not None:
        type_eq = db.query(models.TypeEquipement).filter(
            models.TypeEquipement.id == data.type_id
        ).first()
        if not type_eq:
            raise HTTPException(status_code=404, detail="Type d'équipement non trouvé")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(equipement, key, value)

    db.commit()
    db.refresh(equipement)
    return equipement


# --------- Ajouter des images à un équipement ---------
@router.post("/{equipement_id}/images", response_model=schemas.EquipementOut)
def ajouter_images(
    equipement_id: int,
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    equipement = db.query(models.Equipement).filter(
        models.Equipement.id == equipement_id
    ).first()
    if not equipement:
        raise HTTPException(status_code=404, detail="Equipement non trouvé")

    for img in images:
        if img.filename:
            chemin = sauvegarder_image(img)
            db.add(models.ImageEquipement(
                equipement_id=equipement.id,
                chemin=chemin
            ))
    db.commit()
    db.refresh(equipement)
    return equipement


# --------- Supprimer une image ---------
@router.delete("/images/{image_id}")
def supprimer_image(
    image_id: int,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    image = db.query(models.ImageEquipement).filter(
        models.ImageEquipement.id == image_id
    ).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image non trouvée")

    # Supprimer le fichier physique
    chemin_physique = image.chemin.lstrip("/")
    if os.path.exists(chemin_physique):
        os.remove(chemin_physique)

    db.delete(image)
    db.commit()
    return {"message": "Image supprimée"}


# --------- Désactiver un équipement (soft delete) ---------
@router.delete("/{equipement_id}")
def desactiver_equipement(
    equipement_id: int,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    equipement = db.query(models.Equipement).filter(
        models.Equipement.id == equipement_id
    ).first()
    if not equipement:
        raise HTTPException(status_code=404, detail="Equipement non trouvé")

    equipement.actif = False
    db.commit()
    return {"message": "Equipement désactivé"}
