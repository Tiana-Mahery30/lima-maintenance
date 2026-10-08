"""
Nettoie tous les signalements existants, puis crée de nouveaux
signalements réalistes sur les équipements actuels.

Usage : python seed_signalements.py
"""
from datetime import datetime, timedelta
from app.database import SessionLocal
from app import models


def clean():
    """Supprime tous les signalements + commentaires + notifications."""
    db = SessionLocal()
    try:
        nb_commentaires = db.query(models.Commentaire).count()
        nb_notifs = db.query(models.Notification).count()
        nb_interventions = db.query(models.Intervention).count()

        db.query(models.Commentaire).delete()
        db.query(models.Notification).delete()
        db.query(models.Intervention).delete()
        db.commit()

        print(f"🗑️  Supprimé : {nb_interventions} interventions, "
              f"{nb_commentaires} commentaires, {nb_notifs} notifications")
    finally:
        db.close()


def seed():
    db = SessionLocal()
    try:
        # ---------- Récupérer les données nécessaires ----------
        employes = db.query(models.Utilisateur).filter(
            models.Utilisateur.role == "employe"
        ).all()

        if not employes:
            print("❌ Aucun employé. Créez-en un d'abord.")
            return

        equipements = {e.numero_serie: e for e in db.query(models.Equipement).all()}
        priorités = {p.nom: p for p in db.query(models.Priorite).all()}

        if not equipements:
            print("❌ Aucun équipement. Lancez d'abord seed_equipements_images.py")
            return

        prio_basse = priorités.get("Basse")
        prio_normale = priorités.get("Normale")
        prio_urgente = priorités.get("Urgente")

        # ---------- Signalements ----------
        now = datetime.utcnow()

        signalements = [
            # ---- TERMINÉS (historique) ----
            {
                "employe": 0, "equipement": "PC-HP-001",
                "priorite": prio_normale,
                "description": "L'ordinateur met plus de 10 minutes à démarrer, il rame énormément.",
                "statut": "terminee",
                "date_signalement": now - timedelta(days=35),
                "date_prise_en_charge": now - timedelta(days=35, hours=-1),
                "date_fin": now - timedelta(days=34),
                "actions_realisees": "Nettoyage complet du disque, désinstallation de logiciels inutiles, ajout de 8 Go de RAM.",
                "resultat": "Démarrage en 1 minute, performances normales."
            },
            {
                "employe": 1, "equipement": "IMP-HP-001",
                "priorite": prio_normale,
                "description": "L'imprimante refuse d'imprimer en couleur, tout sort en noir et blanc.",
                "statut": "terminee",
                "date_signalement": now - timedelta(days=22),
                "date_prise_en_charge": now - timedelta(days=22, hours=-2),
                "date_fin": now - timedelta(days=21),
                "actions_realisees": "Remplacement des cartouches couleur vides.",
                "resultat": "Impression couleur fonctionnelle."
            },
            {
                "employe": 2, "equipement": "SCN-EP-001",
                "priorite": prio_basse,
                "description": "Le scanner fait un bruit strident quand il scanne.",
                "statut": "terminee",
                "date_signalement": now - timedelta(days=18),
                "date_prise_en_charge": now - timedelta(days=17),
                "date_fin": now - timedelta(days=16),
                "actions_realisees": "Nettoyage du mécanisme interne, lubrification légère.",
                "resultat": "Plus de bruit anormal, scan normal."
            },
            {
                "employe": 0, "equipement": "CLA-LG-001",
                "priorite": prio_basse,
                "description": "Certaines touches ne répondent plus (Espace, Entrée).",
                "statut": "terminee",
                "date_signalement": now - timedelta(days=12),
                "date_prise_en_charge": now - timedelta(days=12, hours=-3),
                "date_fin": now - timedelta(days=11),
                "actions_realisees": "Remplacement du clavier défectueux par un neuf.",
                "resultat": "Clavier neuf, toutes les touches fonctionnent."
            },
            {
                "employe": 1, "equipement": "SOU-LG-001",
                "priorite": prio_basse,
                "description": "Le clic gauche de la souris fonctionne une fois sur deux.",
                "statut": "terminee",
                "date_signalement": now - timedelta(days=8),
                "date_prise_en_charge": now - timedelta(days=8, hours=-1),
                "date_fin": now - timedelta(days=7),
                "actions_realisees": "Remplacement de la souris.",
                "resultat": "Nouvelle souris, clic fonctionnel."
            },

            # ---- EN COURS ----
            {
                "employe": 2, "equipement": "IMP-CN-002",
                "priorite": prio_urgente,
                "description": "Bourrage papier constant. L'imprimante bloque à chaque impression.",
                "statut": "en_cours",
                "date_signalement": now - timedelta(days=3),
                "date_prise_en_charge": now - timedelta(days=2),
            },
            {
                "employe": 0, "equipement": "OND-AP-001",
                "priorite": prio_normale,
                "description": "L'onduleur bipe en permanence même quand le courant est stable.",
                "statut": "en_cours",
                "date_signalement": now - timedelta(days=2),
                "date_prise_en_charge": now - timedelta(days=1),
            },
            {
                "employe": 1, "equipement": "ROU-TP-001",
                "priorite": prio_urgente,
                "description": "Le WiFi coupe toutes les 10 minutes dans tout le bureau.",
                "statut": "en_cours",
                "date_signalement": now - timedelta(days=1, hours=6),
                "date_prise_en_charge": now - timedelta(hours=20),
            },

            # ---- EN ATTENTE (récents) ----
            {
                "employe": 2, "equipement": "PC-HP-001",
                "priorite": prio_normale,
                "description": "L'écran s'éteint tout seul pendant 2 secondes puis se rallume.",
                "statut": "en_attente",
                "date_signalement": now - timedelta(hours=5),
            },
            {
                "employe": 0, "equipement": "ECR-SM-001",
                "priorite": prio_basse,
                "description": "Il y a une ligne verticale rose sur le côté gauche de l'écran.",
                "statut": "en_attente",
                "date_signalement": now - timedelta(hours=3),
            },
            {
                "employe": 1, "equipement": "CLA-MS-002",
                "priorite": prio_normale,
                "description": "La touche É ne fonctionne plus correctement, il faut appuyer très fort.",
                "statut": "en_attente",
                "date_signalement": now - timedelta(hours=2),
            },
            {
                "employe": 2, "equipement": "SCN-CN-002",
                "priorite": prio_normale,
                "description": "Le scanner n'est plus détecté par l'ordinateur.",
                "statut": "en_attente",
                "date_signalement": now - timedelta(hours=1),
            },

            # ---- EN RETARD (dépassement 48h) ----
            {
                "employe": 0, "equipement": "ECR-LG-002",
                "priorite": prio_normale,
                "description": "L'image scintille fortement, surtout sur les fonds sombres.",
                "statut": "en_attente",
                "date_signalement": now - timedelta(days=4),
            },
            {
                "employe": 1, "equipement": "OND-EA-002",
                "priorite": prio_urgente,
                "description": "L'onduleur ne tient plus la charge, l'ordinateur s'éteint immédiatement en cas de coupure.",
                "statut": "en_attente",
                "date_signalement": now - timedelta(days=6),
            },
        ]

        crees = 0
        for s in signalements:
            equipement = equipements.get(s["equipement"])
            if not equipement:
                print(f"⚠️  Équipement '{s['equipement']}' introuvable, ignoré")
                continue

            employe = employes[s["employe"] % len(employes)]

            intervention = models.Intervention(
                utilisateur_id=employe.id,
                equipement_id=equipement.id,
                priorite_id=s["priorite"].id if s["priorite"] else None,
                description_panne=s["description"],
                statut=s["statut"],
                date_signalement=s["date_signalement"],
                date_prise_en_charge=s.get("date_prise_en_charge"),
                date_fin=s.get("date_fin"),
                actions_realisees=s.get("actions_realisees"),
                resultat=s.get("resultat"),
            )
            db.add(intervention)
            crees += 1

        db.commit()
        print(f"\n✅ {crees} signalements créés")
        print(f"   - {sum(1 for s in signalements if s['statut'] == 'terminee')} terminés")
        print(f"   - {sum(1 for s in signalements if s['statut'] == 'en_cours')} en cours")
        print(f"   - {sum(1 for s in signalements if s['statut'] == 'en_attente')} en attente")

    finally:
        db.close()


if __name__ == "__main__":
    print("=== Nettoyage ===\n")
    clean()
    print("\n=== Nouveaux signalements ===\n")
    seed()
    print("\n🎉 Terminé.")
