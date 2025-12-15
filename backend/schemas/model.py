from pydantic import BaseModel
from typing import Optional, Dict, Any


class ModelBase(BaseModel):
    name: str
    catalog_id: Optional[str] = None
    type: str
    category: Optional[str] = None
    file_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    dimensions: Optional[Dict[str, float]] = None
    position: Optional[Dict[str, float]] = None
    rotation: Optional[Dict[str, float]] = None
    scale: Optional[Dict[str, float]] = None


class ModelCreate(ModelBase):
    room_id: Optional[int] = None
    project_id: Optional[int] = None
    material_id: Optional[int] = None


class ModelUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    category: Optional[str] = None
    file_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    dimensions: Optional[Dict[str, float]] = None
    position: Optional[Dict[str, float]] = None
    rotation: Optional[Dict[str, float]] = None
    scale: Optional[Dict[str, float]] = None
    material_id: Optional[int] = None


class ModelResponse(ModelBase):
    id: int
    room_id: Optional[int] = None
    project_id: Optional[int] = None
    material_id: Optional[int] = None

    class Config:
        from_attributes = True
