from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    content: str
    username: str
    room_id: int

class MessageOut(BaseModel):
    id: int
    content: str
    username: str
    timestamp: datetime
    room_id: int

    model_config = {
        "from_attributes": True
    }

class RoomCreate(BaseModel):
    name: str

class RoomOut(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }
# For creating a room
class ChatRoomCreate(BaseModel):
    name: str
# For returning room info
class ChatRoomOut(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True
