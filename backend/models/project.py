from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


class Project(Base):
    """
    Модель Проект из диаграммы классов
    Attributes:
        - идПроекта: int
        - название: string
        - описание: string
        - модель: Модель
    Methods:
        - добавитьМодельДляПланировки(list<Модель>): void
        - создатьМодельДляДизайнера(int, Модель): Модель
    """
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="active")  # active, completed, archived
    
    # Связь с пользователем (клиентом)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="projects", foreign_keys=[user_id])
    
    # Связь с дизайнером (опционально)
    designer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    designer = relationship("User", back_populates="assigned_projects", foreign_keys=[designer_id])
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rooms = relationship("Room", back_populates="project", cascade="all, delete-orphan")
    models = relationship("Model", back_populates="project")
    recommendations = relationship("Recommendation", back_populates="project")
    comments = relationship("Comment", back_populates="project")
    analysis_results = relationship("AnalysisResult", back_populates="project")

    def __repr__(self):
        return f"<Project {self.name}>"
