from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from typing import List
from jose import jwt, JWTError

from ..database import get_db, SessionLocal
from .. import models, schemas
from ..auth import require_authentifie, SECRET_KEY, ALGORITHM
from ..websocket import manager

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# Lister mes notifications
@router.get("/", response_model=List[schemas.NotificationOut])
def mes_notifications(
    db: Session = Depends(get_db),
    utilisateur: models.Utilisateur = Depends(require_authentifie)
):
    return db.query(models.Notification).filter(
        models.Notification.utilisateur_id == utilisateur.id
    ).order_by(models.Notification.date.desc()).limit(50).all()


# Compter les notifications non lues
@router.get("/non-lues/count")
def compter_non_lues(
    db: Session = Depends(get_db),
    utilisateur: models.Utilisateur = Depends(require_authentifie)
):
    count = db.query(models.Notification).filter(
        models.Notification.utilisateur_id == utilisateur.id,
        models.Notification.lu == False
    ).count()
    return {"count": count}


# Marquer une notification comme lue
@router.put("/{notification_id}/lire")
def marquer_lue(
    notification_id: int,
    db: Session = Depends(get_db),
    utilisateur: models.Utilisateur = Depends(require_authentifie)
):
    notif = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.utilisateur_id == utilisateur.id
    ).first()
    if not notif:
        return {"message": "Notification non trouvée"}
    notif.lu = True
    db.commit()
    return {"message": "Notification marquée comme lue"}


# Marquer toutes comme lues
@router.put("/tout-lire")
def marquer_tout_lu(
    db: Session = Depends(get_db),
    utilisateur: models.Utilisateur = Depends(require_authentifie)
):
    db.query(models.Notification).filter(
        models.Notification.utilisateur_id == utilisateur.id,
        models.Notification.lu == False
    ).update({"lu": True})
    db.commit()
    return {"message": "Toutes les notifications marquées comme lues"}


# ---------- WebSocket temps réel ----------
@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    Connexion WebSocket : ws://127.0.0.1:8000/notifications/ws?token=JWT
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        await websocket.close(code=1008)
        return

    db = SessionLocal()
    try:
        utilisateur = db.query(models.Utilisateur).filter(
            models.Utilisateur.email == email
        ).first()
        if not utilisateur:
            await websocket.close(code=1008)
            return

        await manager.connect(utilisateur.id, websocket)
        try:
            while True:
                # On attend les messages du client (ping par ex.)
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(utilisateur.id, websocket)
    finally:
        db.close()
