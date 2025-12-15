from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List


class RecommendationBase(BaseModel):
    text: str
    type: str  # layout, material, style, optimization
    priority: str = "medium"  # low, medium, high


class RecommendationCreate(RecommendationBase):
    project_id: int
    confidence_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class RecommendationUpdate(BaseModel):
    text: Optional[str] = None
    type: Optional[str] = None
    priority: Optional[str] = None
    is_applied: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class RecommendationResponse(RecommendationBase):
    id: int
    project_id: int
    confidence_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    is_applied: int
    created_at: datetime

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    status: str = "pending"
    priority: str = "medium"
    dimensions: Optional[Dict[str, Any]] = None
    quality_parameters: Optional[Dict[str, Any]] = None


class TaskCreate(TaskBase):
    model_id: Optional[int] = None
    room_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    dimensions: Optional[Dict[str, Any]] = None
    quality_parameters: Optional[Dict[str, Any]] = None


class TaskResponse(TaskBase):
    id: int
    model_id: Optional[int] = None
    room_id: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
