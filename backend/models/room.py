from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship

from ..database import Base


class Room(Base):
    """
    Модель Помещение из диаграммы (часть подсистемы моделирования)
    Связана с проектом и содержит параметры помещения
    """
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Название комнаты (Гостиная, Кухня, etc.)
    
    # Размеры помещения
    width = Column(Float, nullable=False)  # Ширина
    length = Column(Float, nullable=False)  # Длина
    height = Column(Float, nullable=False)  # Высота
    area = Column(Float)  # Площадь (автоматически вычисляется)
    
    # Связь с проектом
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="rooms")
    
    # 3D координаты и параметры
    position = Column(JSON)  # {x, y, z}
    rotation = Column(JSON)  # {x, y, z} углы поворота
    
    # Relationships
    models = relationship("Model", back_populates="room")
    tasks = relationship("Task", back_populates="room")

    def __repr__(self):
        return f"<Room {self.name} ({self.width}x{self.length}m)>"
