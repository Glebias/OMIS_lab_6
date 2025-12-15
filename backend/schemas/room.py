from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any


class RoomBase(BaseModel):
    name: str
    width: float
    length: float
    height: float
    position: Optional[Dict[str, float]] = None
    rotation: Optional[Dict[str, float]] = None

    @field_validator('width', 'length', 'height')
    @classmethod
    def validate_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Размеры должны быть положительными')
        return v


class RoomCreate(RoomBase):
    project_id: int


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    width: Optional[float] = None
    length: Optional[float] = None
    height: Optional[float] = None
    position: Optional[Dict[str, float]] = None
    rotation: Optional[Dict[str, float]] = None


class RoomResponse(RoomBase):
    id: int
    project_id: int
    area: Optional[float] = None

    class Config:
        from_attributes = True
