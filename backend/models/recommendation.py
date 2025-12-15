from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


class Recommendation(Base):
    """
    Модель Рекомендация из диаграммы
    Attributes:
        - идРекомендации: int
        - текст: string
        - тип: string
    """
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    type = Column(String, nullable=False)  # layout, material, style, optimization
    priority = Column(String, default="medium")  # low, medium, high
    
    # Связь с проектом
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="recommendations")
    
    # AI-генерированные данные
    confidence_score = Column(Float)  # Уверенность рекомендации (0-1)
    metadata = Column(JSON)  # Дополнительные данные от LLM
    
    is_applied = Column(Integer, default=0)  # Применена ли рекомендация
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Recommendation {self.type} for Project {self.project_id}>"


class Task(Base):
    """
    Модель Задание из диаграммы
    Attributes:
        - размер: list<int>
        - категория: string
        - качество: list<string>
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    
    # Связь с моделью
    model_id = Column(Integer, ForeignKey("models.id"), nullable=True)
    model = relationship("Model", back_populates="tasks")
    
    # Связь с помещением
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    room = relationship("Room", back_populates="tasks")
    
    status = Column(String, default="pending")  # pending, in_progress, completed
    priority = Column(String, default="medium")
    
    dimensions = Column(JSON)  # Размерные требования
    quality_parameters = Column(JSON)  # Параметры качества
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Task {self.title} ({self.status})>"
