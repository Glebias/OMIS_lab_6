from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ChatMessageBase(BaseModel):
    message: str
    recipient_id: Optional[int] = None
    project_id: Optional[int] = None


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageResponse(ChatMessageBase):
    id: int
    sender_id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ConsultationBase(BaseModel):
    topic: str
    description: Optional[str] = None
    project_id: Optional[int] = None


class ConsultationCreate(ConsultationBase):
    pass


class ConsultationUpdate(BaseModel):
    topic: Optional[str] = None
    description: Optional[str] = None
    consultant_id: Optional[int] = None
    status: Optional[str] = None


class ConsultationResponse(ConsultationBase):
    id: int
    client_id: int
    consultant_id: Optional[int] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    text: str
    project_id: int


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
