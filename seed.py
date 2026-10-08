"""
Script d'initialisation : crée les données de base.
À exécuter UNE FOIS après avoir créé la base.

Usage : python seed.py
"""
from app.database import SessionLocal
from app import models
from app.auth import hasher_mot_de_passe


def seed():
    db = SessionLocal()
    try:
        # --- Services ---
        services = ["Direction", "Comptabilité", "Ressources Humaines",
                    "Commercial", "Informatique"]
        for nom in services:
            if not db.query(models.Service).filter(models.Service.nom == nom).first():
                db.add(models.Service(nom=nom))
        db.commit()
        print(f"✅ {len(services)} services prêts")

        # --- Types d'équipement ---
        types_eq = ["PC", "Imprimante", "Scanner", "Écran",
                    "Clavier", "Souris", "Onduleur", "Routeur"]
        for nom in types_eq:
            if not db.query(models.TypeEquipement).filter(
                models.TypeEquipement.nom == nom
            ).first():
                db.add(models.TypeEquipement(nom=nom))
        db.commit()
        print(f"✅ {len(types_eq)} types d'équipement prêts")

        # --- Priorités ---
        priorites = [
            {"nom": "Basse",   "couleur": "#4CAF50", "ordre": 1},
            {"nom": "Normale", "couleur": "#FFC107", "ordre": 2},
            {"nom": "Urgente", "couleur": "#F44336", "ordre": 3},
        ]
        for p in priorites:
            if not db.query(models.Priorite).filter(
                models.Priorite.nom == p["nom"]
            ).first():
                db.add(models.Priorite(**p))
        db.commit()
        print(f"✅ {len(priorites)} priorités prêtes")

        # --- Technicien par défaut ---
        email_tech = "technicien@lima.mg"
        if not db.query(models.Utilisateur).filter(
            models.Utilisateur.email == email_tech
        ).first():
            service_info = db.query(models.Service).filter(
                models.Service.nom == "Informatique"
            ).first()
            tech = models.Utilisateur(
                nom="Technicien LIMA",
                email=email_tech,
                mot_de_passe=hasher_mot_de_passe("lima2026"),
                role="technicien",
                service_id=service_info.id if service_info else None,
            )
            db.add(tech)
            db.commit()
            print(f"✅ Technicien créé : {email_tech} / lima2026")
        else:
            print("ℹ️  Technicien déjà présent")

        # --- Paramètres ---
        params = [
            {"cle": "delai_alerte_heures", "valeur": "48"},
            {"cle": "max_images_equipement", "valeur": "5"},
        ]
        for p in params:
            if not db.query(models.Parametre).filter(
                models.Parametre.cle == p["cle"]
            ).first():
                db.add(models.Parametre(**p))
        db.commit()
        print(f"✅ {len(params)} paramètres prêts")

        print("\n🎉 Seed terminé avec succès.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
