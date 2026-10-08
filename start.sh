#!/bin/bash

# ============================================================
#   LIMA GROUP - Gestion Maintenance Informatique
#   Script de démarrage (Linux / macOS)
# ============================================================

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   LIMA GROUP - Gestion Maintenance Informatique          ║${NC}"
echo -e "${BLUE}║   Démarrage du serveur                                   ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Se placer dans le dossier du script
cd "$(dirname "$0")"

# ---------- Vérifier Python ----------
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 n'est pas installé.${NC}"
    echo "   Installez-le : sudo apt install python3 python3-venv"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 détecté${NC} : $(python3 --version)"

# ---------- Créer le venv si absent ----------
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Création de l'environnement virtuel...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Environnement virtuel créé${NC}"
fi

# ---------- Activer le venv ----------
echo -e "${BLUE}🔌 Activation de l'environnement virtuel...${NC}"
source venv/bin/activate

# ---------- Vérifier/installer les dépendances ----------
if ! python -c "import fastapi" &> /dev/null; then
    echo -e "${YELLOW}📥 Installation des dépendances...${NC}"
    pip install --upgrade pip > /dev/null
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dépendances installées${NC}"
else
    echo -e "${GREEN}✅ Dépendances déjà présentes${NC}"
fi

# ---------- Vérifier la base de données ----------
if [ ! -f "lima_maintenance.db" ]; then
    echo -e "${YELLOW}🗄️  Base de données absente. Création...${NC}"
    python seed.py

    if [ -f "seed_equipements_images.py" ] && [ -d "EQUIPEMENTS POUR SIMULATION" ]; then
        echo -e "${BLUE}📷 Ajout des équipements de démonstration...${NC}"
        python seed_equipements_images.py
    fi

    if [ -f "seed_signalements.py" ]; then
        echo -e "${BLUE}📝 Ajout des signalements de démonstration...${NC}"
        python seed_signalements.py
    fi

    echo -e "${GREEN}✅ Base de données initialisée${NC}"
else
    echo -e "${GREEN}✅ Base de données existante${NC}"
fi

# ---------- Créer les dossiers d'upload si absents ----------
mkdir -p static/uploads/equipements
mkdir -p static/uploads/interventions
mkdir -p static/uploads/profils

# ---------- Récupérer l'IP locale ----------
IP_LOCALE=$(hostname -I 2>/dev/null | awk '{print $1}')
if [ -z "$IP_LOCALE" ]; then
    IP_LOCALE="127.0.0.1"
fi

# ---------- Lancer uvicorn ----------
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   🚀 Serveur en cours de démarrage...                    ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "   ${BLUE}Local${NC}   : http://127.0.0.1:8000"
echo -e "   ${BLUE}Réseau${NC}  : http://$IP_LOCALE:8000"
echo -e "   ${BLUE}API Docs${NC}: http://127.0.0.1:8000/docs"
echo ""
echo -e "   ${YELLOW}Comptes de test :${NC}"
echo -e "     Technicien : technicien@lima.mg / kamil2026"
echo -e "     Employé    : kamil@lima.mg / kamil2026"
echo -e "     Employé    : marie@lima.mg / employe2026"
echo ""
echo -e "   ${YELLOW}Appuyez sur Ctrl+C pour arrêter${NC}"
echo ""

# Lancer en mode reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
