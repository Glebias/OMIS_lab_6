from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship

from ..database import Base


class Model(Base):
    """
    Модель из диаграммы классов
    Attributes:
        - идМодели: int
        - каталог: string
        - размер: list<int>
        - тип: string
        - название: list<Мебель>
        - задание: list<Задание>
    Methods:
        - выбратьВариантРазмер(вариант: int): void
    """
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    catalog_id = Column(String)  # ID из каталога
    type = Column(String, nullable=False)  # furniture, fixture, decoration
    category = Column(String)  # kitchen, bathroom, living_room, bedroom
    
    # 3D данные модели
    file_url = Column(String)  # URL к .glb/.obj файлу
    thumbnail_url = Column(String)  # Превью модели
    
    # Размеры модели (в метрах)
    dimensions = Column(JSON)  # {width, height, depth}
    
    # Связь с помещением и проектом
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    room = relationship("Room", back_populates="models")
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    project = relationship("Project", back_populates="models")
    
    # Позиция в 3D пространстве
    position = Column(JSON)  # {x, y, z}
    rotation = Column(JSON)  # {x, y, z}
    scale = Column(JSON)  # {x, y, z}
    
    # Связь с материалами
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=True)
    material = relationship("Material", back_populates="models")
    
    # Relationships
    tasks = relationship("Task", back_populates="model")

    def __repr__(self):
        return f"<Model {self.name} ({self.type})>"
