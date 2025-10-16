# from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
# from sqlalchemy.orm import Session
# from db import get_db
# import models, schemas
# from websocket_manager import manager

# router = APIRouter(prefix="/chat", tags=["Chat"])

# # ✅ Create room
# @router.post("/rooms", response_model=schemas.ChatRoomOut)
# def create_room(room: schemas.ChatRoomCreate, db: Session = Depends(get_db)):
#     db_room = models.ChatRoom(name=room.name)
#     db.add(db_room)
#     db.commit()
#     db.refresh(db_room)
#     return db_room

# # ✅ List rooms
# @router.get("/rooms", response_model=list[schemas.ChatRoomOut])
# def list_rooms(db: Session = Depends(get_db)):
#     return db.query(models.ChatRoom).all()

# # ✅ Join a room (REST)
# @router.post("/rooms/{room_name}/join")
# def join_room(room_name: str, username: str, db: Session = Depends(get_db)):
#     room = db.query(models.ChatRoom).filter_by(name=room_name).first()
#     if not room:
#         raise HTTPException(status_code=404, detail="Room not found")
#     return {"message": f"{username} joined {room_name}", "room": room_name, "username": username}

# # ✅ List members (demo)
# @router.get("/rooms/{room_name}/members")
# def get_room_members(room_name: str):
#     # 🔹 For simplicity, we track members only in memory (via websocket_manager)
#     members = manager.active_connections.get(room_name, [])
#     return {"room": room_name, "members": len(members)}



#ws-websocket
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from db import get_db
import models, schemas
from websocket_manager import manager

router = APIRouter(prefix="/chat", tags=["Chat"])

# ✅ Create room
@router.post("/rooms", response_model=schemas.ChatRoomOut)
def create_room(room: schemas.ChatRoomCreate, db: Session = Depends(get_db)):
    db_room = models.ChatRoom(name=room.name)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

# ✅ List rooms
@router.get("/rooms", response_model=list[schemas.ChatRoomOut])
def list_rooms(db: Session = Depends(get_db)):
    return db.query(models.ChatRoom).all()

# ✅ Join a room (REST - just acknowledgment, no WebSocket connection yet)
@router.post("/rooms/{room_name}/join")
def join_room(room_name: str, username: str, db: Session = Depends(get_db)):
    room = db.query(models.ChatRoom).filter_by(name=room_name).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"message": f"{username} joined {room_name}", "room": room_name, "username": username}

# ✅ List members (via websocket_manager)
@router.get("/rooms/{room_name}/members")
def get_room_members(room_name: str):
    members = manager.get_members(room_name)
    return {"room": room_name, "members": members, "count": len(members)}

@router.websocket("/ws/{room_name}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_name: str, username: str):
    db = next(get_db())  # manually create DB session
    await manager.connect(room_name, username, websocket)
    try:
        await manager.broadcast(room_name, f"🟢 {username} joined {room_name}")
        while True:
            data = await websocket.receive_text()
            # Save message to DB
            room = db.query(models.ChatRoom).filter_by(name=room_name).first()
            if room:
                db_message = models.Message(
                    room_id=room.id,
                    username=username,
                    content=data
                )
                db.add(db_message)
                db.commit()
            await manager.broadcast(room_name, f"{username}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(room_name, websocket)
        await manager.broadcast(room_name, f"🔴 {username} left {room_name}")
    finally:
        db.close()
