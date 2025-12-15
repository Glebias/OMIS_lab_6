from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


class AnalysisResult(Base):
    """
    Результаты анализа планировки из подсистемы анализа
    """
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    
    # Связь с проектом
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="analysis_results")
    
    # Тип анализа
    analysis_type = Column(String, nullable=False)  # layout, lighting, ergonomics, cost
    
    # Результаты
    score = Column(Float)  # Общий балл (0-100)
    status = Column(String)  # good, warning, critical
    
    # Детали анализа
    details = Column(JSON)  # Подробные результаты
    issues = Column(JSON)  # Обнаруженные проблемы
    suggestions = Column(JSON)  # Предложения по улучшению
    
    # AI-генерированный отчет
    report = Column(Text)  # Текстовый отчет
    
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AnalysisResult {self.analysis_type} for Project {self.project_id}>"
