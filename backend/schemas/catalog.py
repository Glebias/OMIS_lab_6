from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class MaterialBase(BaseModel):
    name: str
    type: str
    texture_url: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    texture_url: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


class MaterialResponse(MaterialBase):
    id: int

    class Config:
        from_attributes = True


class StandardBase(BaseModel):
    name: str
    code: str
    category: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class StandardCreate(StandardBase):
    material_id: Optional[int] = None


class StandardUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    material_id: Optional[int] = None


class StandardResponse(StandardBase):
    id: int
    material_id: Optional[int] = None

    class Config:
        from_attributes = True


class CatalogBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CatalogCreate(CatalogBase):
    pass


class CatalogUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    items_count: Optional[int] = None


class CatalogResponse(CatalogBase):
    id: int
    items_count: int

    class Config:
        from_attributes = True
