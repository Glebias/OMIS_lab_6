from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


class ChatMessage(Base):
    """Модель для системы чата/консультаций"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    
    # Отправитель
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sender = relationship("User", back_populates="chat_messages", foreign_keys=[sender_id])
    
    # Получатель (для приватных чатов)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Связь с проектом (если сообщение относится к проекту)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # Содержимое
    message = Column(Text, nullable=False)
    
    # Метаданные
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ChatMessage from User {self.sender_id}>"


class Consultation(Base):
    """Модель для запросов на консультацию"""
    __tablename__ = "consultations"

    id = Column(Integer, primary_key=True, index=True)
    
    # Клиент
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client = relationship("User", back_populates="consultations", foreign_keys=[client_id])
    
    # Консультант/Дизайнер (назначается позже)
    consultant_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Связь с проектом
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    topic = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="pending")  # pending, assigned, in_progress, completed
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Consultation {self.topic} ({self.status})>"


class Comment(Base):
    """Комментарии к проектам"""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    
    # Автор
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="comments")
    
    # Проект
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="comments")
    
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Comment on Project {self.project_id}>"
