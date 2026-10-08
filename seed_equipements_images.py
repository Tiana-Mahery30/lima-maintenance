"""
Ajoute des équipements avec leurs images depuis le dossier
'EQUIPEMENTS POUR SIMULATION'.

Usage : python seed_equipements_images.py
"""
import os
import shutil
import uuid
from datetime import date
from app.database import SessionLocal
from app import models

DOSSIER_SOURCE = "EQUIPEMENTS POUR SIMULATION"
DOSSIER_DEST = "static/uploads/equipements"

# Correspondance : fichier image → (type, marque, modèle, numéro série, date acquisition)
EQUIPEMENTS = [
    # (fichier, nom_type, marque, modele, numero_serie, date_acq)
    ("PC1.jpeg",          "PC",         "HP",       "EliteDesk 800",   "PC-HP-001",     date(2022, 3, 15)),
    ("IMPRIMANTE1.jpeg",  "Imprimante", "HP",       "LaserJet Pro",    "IMP-HP-001",    date(2021, 6, 10)),
    ("IMPRIMANTE2.jpeg",  "Imprimante", "Canon",    "PIXMA G3420",     "IMP-CN-002",    date(2023, 1, 20)),
    ("SCANNER1.jpeg",     "Scanner",    "Epson",    "V39",             "SCN-EP-001",    date(2022, 9, 5)),
    ("SCANNER2.jpeg",     "Scanner",    "Canon",    "CanoScan Lide",   "SCN-CN-002",    date(2023, 4, 12)),
    ("CLAVIER1.jpeg",     "Clavier",    "Logitech", "K120",            "CLA-LG-001",    date(2022, 2, 1)),
    ("CLAVIER2.jpeg",     "Clavier",    "Microsoft","Wired 600",       "CLA-MS-002",    date(2023, 5, 8)),
    ("SOURIS1.jpeg",      "Souris",     "Logitech", "M90",             "SOU-LG-001",    date(2022, 2, 1)),
    ("SOURIS2.jpeg",      "Souris",     "HP",       "X500",            "SOU-HP-002",    date(2023, 7, 14)),
    ("ONDULEUR1.jpeg",    "Onduleur",   "APC",      "Back-UPS 650",    "OND-AP-001",    date(2021, 11, 3)),
    ("ONDULEUR2.jpeg",    "Onduleur",   "Eaton",    "5E 650i",         "OND-EA-002",    date(2022, 8, 20)),
    ("ROUTER1.jpeg",      "Routeur",    "TP-Link",  "Archer C6",       "ROU-TP-001",    date(2023, 3, 1)),
    ("ROUTEUR2.jpeg",     "Routeur",    "Netgear",  "Nighthawk R7000", "ROU-NG-002",    date(2023, 6, 15)),
    ("TV1.jpeg",          "Écran",      "Samsung",  "UE43T5300",       "ECR-SM-001",    date(2024, 1, 10)),
    ("TV2.jpeg",          "Écran",      "LG",       "43UM7100",        "ECR-LG-002",    date(2024, 2, 22)),
]


def creer_image(equipement_id, chemin_source, db):
    """Copie une image et crée l'enregistrement."""
    if not os.path.exists(chemin_source):
        print(f"  ⚠️  Image manquante : {chemin_source}")
        return False

    ext = os.path.splitext(chemin_source)[1].lower()
    nom_unique = f"{uuid.uuid4().hex}{ext}"
    chemin_dest = os.path.join(DOSSIER_DEST, nom_unique)

    shutil.copy2(chemin_source, chemin_dest)

    image = models.ImageEquipement(
        equipement_id=equipement_id,
        chemin=f"/{chemin_dest}"
    )
    db.add(image)
    return True


def seed():
    if not os.path.exists(DOSSIER_SOURCE):
        print(f"❌ Dossier introuvable : {DOSSIER_SOURCE}")
        return

    os.makedirs(DOSSIER_DEST, exist_ok=True)

    db = SessionLocal()
    try:
        # Charger les types
        types_map = {t.nom: t.id for t in db.query(models.TypeEquipement).all()}

        crees = 0
        ignores = 0
        images_ajoutees = 0

        for fichier, nom_type, marque, modele, numero_serie, date_acq in EQUIPEMENTS:
            # Vérifier si l'équipement existe déjà
            existe = db.query(models.Equipement).filter(
                models.Equipement.numero_serie == numero_serie
            ).first()
            if existe:
                print(f"⏭️  {numero_serie} existe déjà, ignoré")
                ignores += 1
                continue

            # Récupérer le type
            type_id = types_map.get(nom_type)
            if not type_id:
                print(f"⚠️  Type '{nom_type}' introuvable, {numero_serie} ignoré")
                ignores += 1
                continue

            # Créer l'équipement
            equipement = models.Equipement(
                type_id=type_id,
                marque=marque,
                modele=modele,
                numero_serie=numero_serie,
                statut="disponible",
                etat="fonctionnel",
                date_acquisition=date_acq,
            )
            db.add(equipement)
            db.commit()
            db.refresh(equipement)

            # Ajouter l'image
            chemin_source = os.path.join(DOSSIER_SOURCE, fichier)
            if creer_image(equipement.id, chemin_source, db):
                images_ajoutees += 1

            db.commit()
            print(f"✅ {numero_serie} — {marque} {modele} ({nom_type}) + image")
            crees += 1

        print(f"\n🎉 Résumé :")
        print(f"   Équipements créés   : {crees}")
        print(f"   Équipements ignorés : {ignores}")
        print(f"   Images ajoutées     : {images_ajoutees}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
