# Guide d'installation — LIMA Maintenance (Windows)

Guide pas à pas pour installer et lancer l'application **LIMA GROUP - Gestion de la maintenance informatique** sur un PC Windows.

---

## Table des matières

1. [Prérequis](#prérequis)
2. [Installation de Python](#installation-de-python)
3. [Installation de Git](#installation-de-git)
4. [Récupération du projet](#récupération-du-projet)
5. [Environnement virtuel](#environnement-virtuel)
6. [Installation des dépendances](#installation-des-dépendances)
7. [Initialisation de la base](#initialisation-de-la-base)
8. [Lancement de l'application](#lancement-de-lapplication)
9. [Comptes de test](#comptes-de-test)
10. [Résolution de problèmes](#résolution-de-problèmes)

---

## Prérequis

- Windows 10 ou 11
- Droits administrateur (pour installer)
- ~500 Mo d'espace disque libre
- Une connexion Internet (pour le premier `pip install`)

---

## Installation de Python

### 1. Télécharger Python

Va sur : **https://www.python.org/downloads/**

Clique sur le gros bouton jaune **"Download Python 3.12.x"**.

### 2. Lancer l'installateur

⚠️ **ÉTAPE CRITIQUE** : dans la première fenêtre, **coche la case** :

```

☑ Add Python to PATH

```
Puis clique sur **"Install Now"**.

### 3. Vérifier l'installation

Ouvre **PowerShell** (touche Windows → tape `powershell` → Entrée) :

```powershell
python --version
```
Doit afficher :

```
Python 3.12.x
```

Si erreur `python n'est pas reconnu` → voir la section Résolution de problèmes.

---

## Installation de Git

### 1. Télécharger Git

Va sur : [**https://git-scm.com/download/win**](https://git-scm.com/download/win)

Le téléchargement démarre automatiquement.

### 2. Lancer l'installateur

Tu peux accepter **toutes les options par défaut**. Clique sur **Next** jusqu'à la fin.

### 3. Vérifier

Ouvre un **nouveau** PowerShell :

```
git --version
```

Doit afficher :

```
git version 2.x.x.windows.x
```

---

## Récupération du projet

### Option A — Depuis GitHub (recommandé)

```
cd C:\Users\TonNom\Documents
git clone https://github.com/TON_USERNAME/lima-maintenance.git
cd lima-maintenance
```

Remplace `TON_USERNAME` par le vrai nom d'utilisateur GitHub.

### Option B — Depuis un ZIP

1. Décompresse l'archive dans `C:\Users\TonNom\Documents\lima-maintenance`
2. Ouvre PowerShell
3. Va dans le dossier :

```
cd C:\Users\TonNom\Documents\lima-maintenance
```

### Vérifier

```
dir
```

Tu dois voir :

```
app
static
templates
requirements.txt
seed.py
README.md
...
```

---

## Environnement virtuel

### 1. Créer l'environnement virtuel

```
python -m venv venv
```

Cela crée un dossier `venv` avec une installation Python isolée.

### 2. Activer l'environnement

```
venv\Scripts\activate
```

⚠️ Sur Windows, c'est `venv\Scripts\activate` (pas `source venv/bin/activate` comme sur Linux).

Une fois activé, tu vois :

```
(venv) PS C:\Users\TonNom\Documents\lima-maintenance>
```

### 3. Mettre à jour pip

```
python -m pip install --upgrade pip
```

---

## Installation des dépendances

```
pip install -r requirements.txt
```

L'installation prend 2 à 5 minutes.

**Résultat attendu** :

```
Successfully installed fastapi-0.115.0 uvicorn-0.32.0 ...
```

### Si erreur avec `bcrypt`

```
pip install bcrypt==4.0.1 --force-reinstall
```

### Si erreur avec `reportlab`

```
pip install reportlab --upgrade
```

### Si erreur avec `cryptography`

```
pip install cryptography --upgrade
```

---

## Initialisation de la base

### Cas 1 — La base est fournie (fichier `lima_maintenance.db` présent)

Passe directement au Lancement.

### Cas 2 — La base n'existe pas

Il faut la créer :

```
python seed.py
```

Puis, si tu as les images des équipements :

```
python seed_equipements_images.py
```

Puis les signalements de démonstration :

```
python seed_signalements.py
```

**Résultat attendu** :

```
✅ 5 services prêts
✅ 8 types d'équipement prêts
✅ 3 priorités prêtes
✅ Technicien créé : technicien@lima.mg / lima2026
🎉 Seed terminé avec succès.
```

---

## Lancement de l'application

### 1. Vérifier que l'environnement est activé

Tu dois voir `(venv)` au début de la ligne :

```
(venv) PS C:\...\lima-maintenance>
```

Si ce n'est pas le cas :

```
venv\Scripts\activate
```

### 2. Lancer le serveur

```
uvicorn app.main:app --reload
```

**Résultat attendu** :

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Application startup complete.
```

### 3. Ouvrir dans le navigateur

Ouvre Chrome / Edge / Firefox et va sur :

[**http://127.0.0.1:8000**](http://127.0.0.1:8000/)

Tu dois voir la page de connexion avec le logo LIMA.

### 4. Arrêter le serveur

Dans le terminal, appuie sur **Ctrl+C**.

---

## Comptes de test

| **Rôle**       | **Email**            | **Mot de passe** |
| :------------- | :------------------- | :--------------- |
| **Technicien** | `technicien@lima.mg` | `kamil2026`       |
| **Employé**    | `kamil@lima.mg`       | `kamil2026`    |
| **Employé**    | `marie@lima.mg`      | `employe2026`    |

---

## Résolution de problèmes

### Problème : `python n'est pas reconnu`

**Cause** : Python n'est pas dans le PATH.

**Solution 1** — Réinstaller Python en cochant **"Add Python to PATH"**.

**Solution 2** — Ajouter manuellement au PATH :

1. Touche Windows → tape `variables d'environnement` → Entrée
2. Clique sur **"Variables d'environnement..."**
3. Dans **"Variables système"**, cherche `Path` → Modifier
4. Ajoute :

```
   C:\Users\TonNom\AppData\Local\Programs\Python\Python312
   C:\Users\TonNom\AppData\Local\Programs\Python\Python312\Scripts
```
5. Redémarre PowerShell

---

### Problème : `venv\Scripts\activate` ne fonctionne pas

**Cause** : PowerShell bloque les scripts par défaut.

**Solution** :

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Confirme avec `O` (Oui). Puis réessaie :

```
venv\Scripts\activate
```

---

### Problème : `uvicorn n'est pas reconnu`

**Cause** : L'environnement virtuel n'est pas activé.

**Solution** :

```
venv\Scripts\activate
uvicorn app.main:app --reload
```

---

### Problème : `ModuleNotFoundError: No module named 'app'`

**Cause** : Tu n'es pas dans le bon dossier.

**Solution** :

```
cd C:\Users\TonNom\Documents\lima-maintenance
dir  # doit lister app, static, templates, etc.
uvicorn app.main:app --reload
```

---

### Problème : `email-validator is not installed`

**Solution** :

```
pip install "pydantic[email]"
```

---

### Problème : `AttributeError: module 'bcrypt' has no attribute '__about__'`

**Solution** :

```
pip uninstall bcrypt -y
pip install bcrypt==4.0.1
```

---

### Problème : `database is locked`

**Cause** : Un processus uvicorn zombie.

**Solution** :

```
taskkill /F /IM python.exe
```

Puis relance.

---

### Problème : Les accents s'affichent bizarrement

**Solution** — Dans PowerShell, avant de lancer :

```
chcp 65001
uvicorn app.main:app --reload
```

Ou change la police du terminal pour une police Unicode (Cascadia Mono, Consolas).

---

### Problème : Le port 8000 est déjà utilisé

**Solution** — Utilise un autre port :

```
uvicorn app.main:app --reload --port 8001
```

Puis ouvre : [**http://127.0.0.1:8001**](http://127.0.0.1:8001/)

---

### Problème : Erreur de connexion WebSocket

**Solution** :

```
pip install websockets --upgrade
```

---

### Problème : Le logo ou les images ne s'affichent pas

**Cause** : Les fichiers uploadés ne sont pas présents.

**Solution** :

Vérifie que ces dossiers existent :

```
static/uploads/equipements/
static/uploads/interventions/
static/img/logo-lima.jpeg
```

Si absent, crée-les :

```
mkdir static\uploads\equipements
mkdir static\uploads\interventions
```

---

### Problème : `ImportError: DLL load failed`

**Cause** : Conflit avec une ancienne installation Python.

**Solution** :

1. Désinstalle Python via **Panneau de configuration**
2. Redémarre Windows
3. Réinstalle Python 3.12 en cochant **"Add to PATH"**

---

## Commandes utiles

| **Action**                  | **Commande**                                                                |
| :-------------------------- | :-------------------------------------------------------------------------- |
| Activer l'environnement     | `venv\Scripts\activate`                                                     |
| Désactiver l'environnement  | `deactivate`                                                                |
| Lancer le serveur           | `uvicorn app.main:app --reload`                                             |
| Arrêter le serveur          | `Ctrl+C`                                                                    |
| Voir les packages installés | `pip list`                                                                  |
| Voir la documentation API   | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)                    |
| Tuer tous les Python        | `taskkill /F /IM python.exe`                                                |
| Vider le cache Python       | `Get-ChildItem -Recurse -Filter __pycache__ \| Remove-Item -Recurse -Force` |

---

## Utilisation quotidienne

### Pour lancer l'appli chaque jour

1. Ouvre PowerShell
2. Va dans le dossier :

```
cd C:\Users\TonNom\Documents\lima-maintenance
```

3. Active l'environnement :

```
venv\Scripts\activate
```

4. Lance le serveur :

```
uvicorn app.main:app --reload
```

5. Ouvre [**http://127.0.0.1:8000**](http://127.0.0.1:8000/) dans ton navigateur

---

## Résumé des étapes

```
1. Installer Python 3.10+ (cocher "Add to PATH")
2. Installer Git
3. Cloner le projet
4. Créer l'environnement virtuel : python -m venv venv
5. Activer : venv\Scripts\activate
6. Installer les dépendances : pip install -r requirements.txt
7. Créer la base : python seed.py
8. Lancer : uvicorn app.main:app --reload
9. Ouvrir : http://127.0.0.1:8000
```

---

## Support

Si tu rencontres un problème non listé :

1. Copie le **message d'erreur exact**
2. Indique la **commande** que tu as tapée
3. Envoie à : [ton email]

---

**LIMA GROUP © 2026**
EOF

```
---

## Ajouter au Git

```
git add GUIDE_WINDOWS.md
git commit -m "Ajout guide d'installation Windows"
git push
```
---



## Ce que ce guide couvre

| **Section**    | **Contenu**                                                     |
| :------------- | :-------------------------------------------------------------- |
| Prérequis      | Windows 10/11, espace disque                                    |
| Python         | Installation + Add to PATH                                      |
| Git            | Installation                                                    |
| Projet         | Clone ou ZIP                                                    |
| Environnement  | `venv` (Windows spécifique)                                     |
| Dépendances    | `pip install` + corrections                                     |
| Base           | `seed.py`, `seed_equipements_images.py`, `seed_signalements.py` |
| Lancement      | `uvicorn`                                                       |
| Comptes        | Technicien + employés                                           |
| **Résolution** | **12 problèmes fréquents avec solutions**                       |
| Commandes      | Tableau récapitulatif                                           |
| Résumé         | 9 étapes condensées                                             |
