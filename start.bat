@echo off
REM ============================================================
REM   LIMA GROUP - Gestion Maintenance Informatique
REM   Script de demarrage (Windows)
REM ============================================================

setlocal

cd /d "%~dp0"

echo.
echo ============================================================
echo   LIMA GROUP - Gestion Maintenance Informatique
echo   Demarrage du serveur
echo ============================================================
echo.

REM ---------- Verifier Python 3.12 via le launcher py ----------
py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python 3.12 n'est pas installe.
    echo.
    echo Telechargez Python 3.12.8 depuis :
    echo   https://www.python.org/downloads/release/python-3128/
    echo.
    echo Pendant l'installation, cochez bien "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('py -3.12 --version') do set PYTHON_VERSION=%%i
echo [OK] %PYTHON_VERSION% detecte
echo.

REM ---------- Creer le venv si absent ----------
if not exist "venv" (
    echo [INFO] Creation de l'environnement virtuel...
    py -3.12 -m venv venv
    if errorlevel 1 (
        echo [ERREUR] Echec de la creation du venv.
        pause
        exit /b 1
    )
    echo [OK] Environnement virtuel cree
    echo.
)

REM ---------- Activer le venv ----------
echo [INFO] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERREUR] Echec de l'activation du venv.
    pause
    exit /b 1
)
echo [OK] Environnement virtuel active
echo.

REM ---------- Verifier/installer les dependances ----------
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installation des dependances...
    python -m pip install --upgrade pip >nul
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERREUR] Echec de l'installation des dependances.
        pause
        exit /b 1
    )
    echo [OK] Dependances installees
) else (
    echo [OK] Dependances deja presentes
)
echo.

REM ---------- Verifier la base de donnees ----------
if not exist "lima_maintenance.db" (
    echo [INFO] Base de donnees absente. Creation...
    python seed.py

    if exist "seed_equipements_images.py" (
        if exist "EQUIPEMENTS POUR SIMULATION" (
            echo [INFO] Ajout des equipements de demonstration...
            python seed_equipements_images.py
        )
    )

    if exist "seed_signalements.py" (
        echo [INFO] Ajout des signalements de demonstration...
        python seed_signalements.py
    )

    echo [OK] Base de donnees initialisee
) else (
    echo [OK] Base de donnees existante
)
echo.

REM ---------- Creer les dossiers d'upload ----------
if not exist "static\uploads\equipements" mkdir "static\uploads\equipements"
if not exist "static\uploads\interventions" mkdir "static\uploads\interventions"
if not exist "static\uploads\profils" mkdir "static\uploads\profils"

REM ---------- Recuperer l'IP locale ----------
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP_LOCALE=%%a
    goto :ip_trouvee
)
:ip_trouvee
set IP_LOCALE=%IP_LOCALE: =%

REM ---------- Lancer uvicorn ----------
echo.
echo ============================================================
echo   Serveur en cours de demarrage...
echo ============================================================
echo.
echo    Local    : http://127.0.0.1:8000
echo    Reseau   : http://%IP_LOCALE%:8000
echo    API Docs : http://127.0.0.1:8000/docs
echo.
echo    Comptes de test :
echo      Technicien : technicien@lima.mg / kamil2026
echo      Employe    : kamil@lima.mg / kamil2026
echo      Employe    : marie@lima.mg / employe2026
echo.
echo    Appuyez sur Ctrl+C pour arreter
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

endlocal
pause
