from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Pages"])
templates = Jinja2Templates(directory="templates")


# ---------- Racine → login ----------
@router.get("/", response_class=HTMLResponse)
def index():
    return RedirectResponse(url="/login")


@router.get("/login", response_class=HTMLResponse)
def page_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# ---------- Interface Employé ----------
@router.get("/employe/dashboard", response_class=HTMLResponse)
def page_employe_dashboard(request: Request):
    return templates.TemplateResponse("employe/dashboard.html", {"request": request})


@router.get("/employe/signaler", response_class=HTMLResponse)
def page_employe_signaler(request: Request):
    return templates.TemplateResponse("employe/signaler.html", {"request": request})


@router.get("/employe/mes-signalements", response_class=HTMLResponse)
def page_employe_mes_signalements(request: Request):
    return templates.TemplateResponse("employe/mes-signalements.html", {"request": request})


@router.get("/employe/equipements", response_class=HTMLResponse)
def page_employe_equipements(request: Request):
    return templates.TemplateResponse("employe/equipements.html", {"request": request})


# ---------- Interface Technicien ----------
@router.get("/technicien/dashboard", response_class=HTMLResponse)
def page_technicien_dashboard(request: Request):
    return templates.TemplateResponse("technicien/dashboard.html", {"request": request})


@router.get("/technicien/signalements", response_class=HTMLResponse)
def page_technicien_signalements(request: Request):
    return templates.TemplateResponse("technicien/signalements.html", {"request": request})


@router.get("/technicien/equipements", response_class=HTMLResponse)
def page_technicien_equipements(request: Request):
    return templates.TemplateResponse("technicien/equipements.html", {"request": request})


@router.get("/technicien/utilisateurs", response_class=HTMLResponse)
def page_technicien_utilisateurs(request: Request):
    return templates.TemplateResponse("technicien/utilisateurs.html", {"request": request})


@router.get("/technicien/statistiques", response_class=HTMLResponse)
def page_technicien_statistiques(request: Request):
    return templates.TemplateResponse("technicien/statistiques.html", {"request": request})


@router.get("/technicien/parametres", response_class=HTMLResponse)
def page_technicien_parametres(request: Request):
    return templates.TemplateResponse("technicien/parametres.html", {"request": request})
