from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, Boolean,
    ForeignKey, Float
)
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


# ---------- 1. Service ----------
class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), unique=True, nullable=False)

    utilisateurs = relationship("Utilisateur", back_populates="service")


# ---------- 2. Utilisateur ----------
class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    mot_de_passe = Column(String(255), nullable=False)   # hash bcrypt
    role = Column(String(20), default="employe")          # employe / technicien
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    actif = Column(Boolean, default=True)
    date_creation = Column(DateTime, default=datetime.utcnow)

    service = relationship("Service", back_populates="utilisateurs")
    affectations = relationship("Affectation", back_populates="utilisateur")
    interventions = relationship(
        "Intervention",
        back_populates="utilisateur",
        foreign_keys="Intervention.utilisateur_id"
    )
    commentaires = relationship("Commentaire", back_populates="auteur")
    notifications = relationship("Notification", back_populates="utilisateur")


# ---------- 3. TypeEquipement ----------
class TypeEquipement(Base):
    __tablename__ = "types_equipement"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), unique=True, nullable=False)   # PC, Imprimante, Scanner...

    equipements = relationship("Equipement", back_populates="type")


# ---------- 4. Equipement ----------
class Equipement(Base):
    __tablename__ = "equipements"

    id = Column(Integer, primary_key=True, index=True)
    type_id = Column(Integer, ForeignKey("types_equipement.id"), nullable=False)
    marque = Column(String(100), nullable=False)
    modele = Column(String(100), nullable=True)
    numero_serie = Column(String(150), unique=True, nullable=False, index=True)

    # statut = disponible / occupé / en maintenance / hors service
    statut = Column(String(30), default="disponible")

    # etat = fonctionnel / en panne
    etat = Column(String(30), default="fonctionnel")

    date_acquisition = Column(Date, nullable=True)
    actif = Column(Boolean, default=True)   # soft delete

    type = relationship("TypeEquipement", back_populates="equipements")
    images = relationship("ImageEquipement", back_populates="equipement", cascade="all, delete-orphan")
    affectations = relationship("Affectation", back_populates="equipement")
    interventions = relationship("Intervention", back_populates="equipement")


# ---------- 5. ImageEquipement ----------
class ImageEquipement(Base):
    __tablename__ = "images_equipement"

    id = Column(Integer, primary_key=True, index=True)
    equipement_id = Column(Integer, ForeignKey("equipements.id"), nullable=False)
    chemin = Column(String(255), nullable=False)
    date_ajout = Column(DateTime, default=datetime.utcnow)

    equipement = relationship("Equipement", back_populates="images")


# ---------- 6. Affectation ----------
class Affectation(Base):
    __tablename__ = "affectations"

    id = Column(Integer, primary_key=True, index=True)
    equipement_id = Column(Integer, ForeignKey("equipements.id"), nullable=False)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    date_debut = Column(DateTime, default=datetime.utcnow)
    date_fin = Column(DateTime, nullable=True)
    actif = Column(Boolean, default=True)   # true = affectation en cours

    equipement = relationship("Equipement", back_populates="affectations")
    utilisateur = relationship("Utilisateur", back_populates="affectations")


# ---------- 7. Priorite ----------
class Priorite(Base):
    __tablename__ = "priorites"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(50), unique=True, nullable=False)   # Basse, Normale, Urgente
    couleur = Column(String(20), default="#999999")
    ordre = Column(Integer, default=0)

    interventions = relationship("Intervention", back_populates="priorite")


# ---------- 8. Intervention ----------
class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, index=True)
    date_signalement = Column(DateTime, default=datetime.utcnow)
    date_prise_en_charge = Column(DateTime, nullable=True)
    date_fin = Column(DateTime, nullable=True)

    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    equipement_id = Column(Integer, ForeignKey("equipements.id"), nullable=False)
    priorite_id = Column(Integer, ForeignKey("priorites.id"), nullable=True)

    description_panne = Column(Text, nullable=False)
    photo_panne = Column(String(255), nullable=True)

    actions_realisees = Column(Text, nullable=True)
    resultat = Column(Text, nullable=True)

    # statut = en_attente / en_cours / terminee
    statut = Column(String(20), default="en_attente")

    archive = Column(Boolean, default=False)   # soft delete

    utilisateur = relationship(
        "Utilisateur", back_populates="interventions",
        foreign_keys=[utilisateur_id]
    )
    equipement = relationship("Equipement", back_populates="interventions")
    priorite = relationship("Priorite", back_populates="interventions")
    commentaires = relationship("Commentaire", back_populates="intervention", cascade="all, delete-orphan")


# ---------- 9. Commentaire ----------
class Commentaire(Base):
    __tablename__ = "commentaires"

    id = Column(Integer, primary_key=True, index=True)
    intervention_id = Column(Integer, ForeignKey("interventions.id"), nullable=False)
    auteur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    contenu = Column(Text, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

    intervention = relationship("Intervention", back_populates="commentaires")
    auteur = relationship("Utilisateur", back_populates="commentaires")


# ---------- 10. Notification ----------
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="info")
    lu = Column(Boolean, default=False)
    date = Column(DateTime, default=datetime.utcnow)

    utilisateur = relationship("Utilisateur", back_populates="notifications")


# ---------- 11. Parametre ----------
class Parametre(Base):
    __tablename__ = "parametres"

    id = Column(Integer, primary_key=True, index=True)
    cle = Column(String(100), unique=True, nullable=False)
    valeur = Column(String(255), nullable=True)
