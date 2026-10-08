# LIMA GROUP — Gestion et suivi de la maintenance informatique

Application web de gestion des interventions informatiques pour **LIMA GROUP** (SARL, Antananarivo, Madagascar).

Elle remplace le suivi dispersé entre WhatsApp et Excel par une plateforme centralisée permettant aux employés de signaler les pannes et au technicien de les traiter efficacement.

---

## Table des matières

1. [Contexte](#contexte)
2. [Fonctionnalités](#fonctionnalités)
3. [Technologies](#technologies)
4. [Installation](#installation)
5. [Lancement](#lancement)
6. [Comptes par défaut](#comptes-par-défaut)
7. [Structure du projet](#structure-du-projet)
8. [API](#api)
9. [Rôles et permissions](#rôles-et-permissions)
10. [Base de données](#base-de-données)
11. [Sauvegarde](#sauvegarde)
12. [Déploiement](#déploiement)
13. [Auteur](#auteur)

---

## Contexte

**Entreprise** : LIMA GROUP
**Activité** : Construction, importation et vente en détail de matériaux de construction, matériels de construction et quincaillerie
**Siège** : Lot 108 NS Ambatmainty, CUA Antananarivo V — Analamanga — Madagascar
**Forme juridique** : SARL (RCS Antananarivo 2023 B 01246)

### Problèmes résolus

- Perte et dispersion des informations entre WhatsApp et Excel
- Difficulté à retrouver l'historique d'un ordinateur
- Absence de suivi en temps réel (en attente / en cours / résolu)
- Risque d'oubli de certaines interventions
- Difficulté à identifier les équipements fréquemment en panne
- Manque de statistiques sur la maintenance

### Objectif

Centraliser les informations relatives aux **équipements**, **utilisateurs**, **pannes** et **interventions** dans une seule plateforme.

---

## Fonctionnalités

### Interface Employé

- Connexion sécurisée (JWT)
- Tableau de bord personnel (statistiques de ses signalements)
- Création d'un signalement de panne avec photo (optionnelle)
- Suivi en temps réel de l'état des signalements
- Commentaires sur ses signalements
- Consultation du parc informatique
- Historique des pannes par équipement
- Notifications temps réel (WebSocket)

### Interface Technicien

- Tableau de bord global (statistiques signalements + équipements)
- Gestion complète des signalements :
  - Voir tous les signalements
  - Filtrer par statut, priorité, employé, équipement
  - Prendre en charge
  - Clôturer avec actions réalisées + résultat
  - Réouvrir si nécessaire
  - Commenter
- Gestion des équipements (CRUD + photos multiples)
- Gestion des utilisateurs (créer, modifier, désactiver)
- Attribution d'équipements aux employés
- Statistiques avec graphiques (Chart.js)
- Export CSV et PDF
- Paramétrage du système (types, services, priorités)

### Notifications temps réel

- WebSocket pour les notifications instantanées
- Badge de compteur dans la sidebar
- Toasts en haut à droite

---

## Technologies

| Couche | Technologie |
|--------|-------------|
| Backend | Python 3.10+, FastAPI |
| Base de données | SQLite + SQLAlchemy 2.0 |
| Authentification | JWT (python-jose) + bcrypt (passlib) |
| Frontend | HTML5 + TailwindCSS (CDN) + JavaScript vanilla |
| Icônes | Lucide Icons |
| Graphiques | Chart.js |
| Export PDF | ReportLab |
| Temps réel | WebSocket (Starlette) |
| Serveur | Uvicorn |

---

## Installation

### Prérequis

- **Python 3.10+**
- **pip**
- Un terminal Linux / macOS / Windows (WSL recommandé)

### Étapes

```bash
# 1. Cloner ou se placer dans le dossier du projet
cd lima_maintenance

# 2. Créer l'environnement virtuel
python -m venv venv

# 3. Activer l'environnement virtuel
source venv/bin/activate          # Linux / macOS
# venv\Scripts\activate           # Windows

# 4. Mettre à jour pip
pip install --upgrade pip

# 5. Installer les dépendances
pip install -r requirements.txt
