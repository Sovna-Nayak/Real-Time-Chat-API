from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # room -> list of (username, WebSocket)
        self.active_connections: Dict[str, List[tuple[str, WebSocket]]] = {}

    async def connect(self, room: str, username: str, websocket: WebSocket):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
        self.active_connections[room].append((username, websocket))

    def disconnect(self, room: str, websocket: WebSocket):
        if room in self.active_connections:
            self.active_connections[room] = [
                (u, ws) for u, ws in self.active_connections[room] if ws != websocket
            ]
            if not self.active_connections[room]:
                del self.active_connections[room]

    # async def broadcast(self, room: str, message: str):
    #     if room in self.active_connections:
    #         for username, connection in self.active_connections[room]:
    #             await connection.send_text(message)
    async def broadcast(self, room: str, message: str):
        if room in self.active_connections:
            to_remove = []
            for username, connection in self.active_connections[room]:
                try:
                    await connection.send_text(message)
                except Exception:
                    # WebSocket closed unexpectedly
                    to_remove.append(connection)
            # Remove closed connections
            self.active_connections[room] = [
                (u, ws) for u, ws in self.active_connections[room] if ws not in to_remove
            ]
            if not self.active_connections[room]:
                del self.active_connections[room]



    def get_members(self, room: str) -> List[str]:
        if room in self.active_connections:
            return [u for u, _ in self.active_connections[room]]
        return []
    
    

manager = ConnectionManager()
