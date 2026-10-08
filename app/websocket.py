from fastapi import WebSocket
from typing import Dict, List


class ConnectionManager:
    """
    Gère les connexions WebSocket.
    Chaque utilisateur connecté est identifié par son id.
    """

    def __init__(self):
        # {utilisateur_id: [WebSocket, ...]}
        self.connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, utilisateur_id: int, websocket: WebSocket):
        await websocket.accept()
        if utilisateur_id not in self.connections:
            self.connections[utilisateur_id] = []
        self.connections[utilisateur_id].append(websocket)
        print(f"🔌 WS connecté : utilisateur {utilisateur_id}")

    def disconnect(self, utilisateur_id: int, websocket: WebSocket):
        if utilisateur_id in self.connections:
            if websocket in self.connections[utilisateur_id]:
                self.connections[utilisateur_id].remove(websocket)
            if not self.connections[utilisateur_id]:
                del self.connections[utilisateur_id]
        print(f"🔌 WS déconnecté : utilisateur {utilisateur_id}")

    async def envoyer_a(self, utilisateur_id: int, message: dict):
        """Envoie un message à un utilisateur précis (toutes ses sessions)."""
        if utilisateur_id in self.connections:
            for ws in list(self.connections[utilisateur_id]):
                try:
                    await ws.send_json(message)
                except Exception:
                    self.disconnect(utilisateur_id, ws)

    async def diffuser_a_tous(self, message: dict):
        """Diffuse un message à tous les utilisateurs connectés."""
        for uid in list(self.connections.keys()):
            await self.envoyer_a(uid, message)

    async def diffuser_par_role(self, role: str, message: dict, db):
        """Diffuse un message à tous les utilisateurs d'un rôle donné."""
        from . import models
        utilisateurs = db.query(models.Utilisateur).filter(
            models.Utilisateur.role == role,
            models.Utilisateur.actif == True
        ).all()
        for u in utilisateurs:
            await self.envoyer_a(u.id, message)


manager = ConnectionManager()
