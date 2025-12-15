from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "active"


class ProjectCreate(ProjectBase):
    designer_id: Optional[int] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    designer_id: Optional[int] = None


class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    designer_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectWithRooms(ProjectResponse):
    rooms: List['RoomResponse'] = []

    class Config:
        from_attributes = True
