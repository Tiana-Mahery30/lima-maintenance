from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from . import models
from .routes import (
    auth, services, types_equipement, priorites,
    utilisateurs, equipements, affectations,
    interventions, commentaires, notifications,
    statistiques, parametres, profil
)
from . import pages

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LIMA GROUP - Gestion Maintenance Informatique",
    description="API de gestion et suivi de la maintenance informatique",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Routes API
app.include_router(auth.router)
app.include_router(services.router)
app.include_router(types_equipement.router)
app.include_router(priorites.router)
app.include_router(utilisateurs.router)
app.include_router(equipements.router)
app.include_router(affectations.router)
app.include_router(interventions.router)
app.include_router(commentaires.router)
app.include_router(notifications.router)
app.include_router(statistiques.router)
app.include_router(parametres.router)
app.include_router(profil.router)

# Pages HTML
app.include_router(pages.router)
