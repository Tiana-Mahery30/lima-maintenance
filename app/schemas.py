from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional, List


# ==================== SERVICE ====================
class ServiceBase(BaseModel):
    nom: str

class ServiceCreate(ServiceBase):
    pass

class ServiceOut(ServiceBase):
    id: int
    class Config:
        from_attributes = True


# ==================== UTILISATEUR ====================
class UtilisateurBase(BaseModel):
    nom: str
    email: EmailStr
    role: Optional[str] = "employe"
    service_id: Optional[int] = None

class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str

class UtilisateurUpdate(BaseModel):
    nom: Optional[str] = None
    email: Optional[EmailStr] = None
    service_id: Optional[int] = None
    actif: Optional[bool] = None

class UtilisateurOut(UtilisateurBase):
    id: int
    actif: bool
    date_creation: datetime
    class Config:
        from_attributes = True


# ==================== AUTH ====================
class LoginData(BaseModel):
    email: EmailStr
    mot_de_passe: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    utilisateur_id: int
    nom: str


# ==================== TYPE EQUIPEMENT ====================
class TypeEquipementBase(BaseModel):
    nom: str

class TypeEquipementCreate(TypeEquipementBase):
    pass

class TypeEquipementOut(TypeEquipementBase):
    id: int
    class Config:
        from_attributes = True


# ==================== EQUIPEMENT ====================
class EquipementBase(BaseModel):
    type_id: int
    marque: str
    modele: Optional[str] = None
    numero_serie: str
    statut: Optional[str] = "disponible"
    etat: Optional[str] = "fonctionnel"
    date_acquisition: Optional[date] = None

class EquipementCreate(EquipementBase):
    pass

class EquipementUpdate(BaseModel):
    type_id: Optional[int] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    numero_serie: Optional[str] = None
    statut: Optional[str] = None
    etat: Optional[str] = None
    date_acquisition: Optional[date] = None

class ImageEquipementOut(BaseModel):
    id: int
    chemin: str
    date_ajout: datetime
    class Config:
        from_attributes = True

class EquipementOut(EquipementBase):
    id: int
    actif: bool
    type: Optional[TypeEquipementOut] = None
    images: List[ImageEquipementOut] = []
    class Config:
        from_attributes = True


# ==================== AFFECTATION ====================
class AffectationCreate(BaseModel):
    equipement_id: int
    utilisateur_id: int

class AffectationOut(BaseModel):
    id: int
    equipement_id: int
    utilisateur_id: int
    date_debut: datetime
    date_fin: Optional[datetime] = None
    actif: bool

    # Relations enrichies
    equipement: Optional[EquipementOut] = None
    utilisateur: Optional[UtilisateurOut] = None

    class Config:
        from_attributes = True


# ==================== PRIORITE ====================
class PrioriteBase(BaseModel):
    nom: str
    couleur: Optional[str] = "#999999"
    ordre: Optional[int] = 0

class PrioriteCreate(PrioriteBase):
    pass

class PrioriteOut(PrioriteBase):
    id: int
    class Config:
        from_attributes = True


# ==================== INTERVENTION ====================
class InterventionBase(BaseModel):
    equipement_id: int
    priorite_id: Optional[int] = None
    description_panne: str

class InterventionCreate(InterventionBase):
    pass

class InterventionUpdate(BaseModel):
    priorite_id: Optional[int] = None
    actions_realisees: Optional[str] = None
    resultat: Optional[str] = None
    statut: Optional[str] = None

class InterventionOut(BaseModel):
    id: int
    date_signalement: datetime
    date_prise_en_charge: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    utilisateur_id: int
    equipement_id: int
    priorite_id: Optional[int] = None
    description_panne: str
    photo_panne: Optional[str] = None
    actions_realisees: Optional[str] = None
    resultat: Optional[str] = None
    statut: str
    archive: bool

    # Relations imbriquées
    priorite: Optional[PrioriteOut] = None
    equipement: Optional[EquipementOut] = None
    utilisateur: Optional[UtilisateurOut] = None

    class Config:
        from_attributes = True


# ==================== COMMENTAIRE ====================
class CommentaireCreate(BaseModel):
    contenu: str

class CommentaireOut(BaseModel):
    id: int
    intervention_id: int
    auteur_id: int
    contenu: str
    date: datetime
    class Config:
        from_attributes = True


# ==================== NOTIFICATION ====================
class NotificationOut(BaseModel):
    id: int
    utilisateur_id: int
    message: str
    type: str
    lu: bool
    date: datetime
    class Config:
        from_attributes = True


# ==================== PARAMETRE ====================
class ParametreBase(BaseModel):
    cle: str
    valeur: Optional[str] = None

class ParametreCreate(ParametreBase):
    pass

class ParametreOut(ParametreBase):
    id: int
    class Config:
        from_attributes = True
