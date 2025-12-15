from sqlalchemy import Column, Integer, String, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class Material(Base):
    """
    Модель Материал из диаграммы
    Attributes:
        - название: string
        - тип: string
        - текстура: string
    """
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # wood, metal, fabric, stone, etc.
    texture_url = Column(String)  # URL текстуры
    
    properties = Column(JSON)  # Дополнительные свойства (цвет, блеск, и т.д.)
    
    # Relationships
    models = relationship("Model", back_populates="material")
    standards = relationship("Standard", back_populates="materials")

    def __repr__(self):
        return f"<Material {self.name} ({self.type})>"


class Standard(Base):
    """
    Модель Стандарт из диаграммы
    Attributes:
        - идСтандарта: int
        - название: string
        - категория: string
    Связан с материалами через отношение
    """
    __tablename__ = "standards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True)  # Код стандарта (например, СНиП)
    category = Column(String, nullable=False)
    
    description = Column(Text)
    parameters = Column(JSON)  # Параметры стандарта
    
    # Связь с материалами
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=True)
    materials = relationship("Material", back_populates="standards")

    def __repr__(self):
        return f"<Standard {self.code}: {self.name}>"


class Catalog(Base):
    """
    Модель Каталог из диаграммы
    Attributes:
        - материалы: string
        - проект: Проект
    Methods:
        - получитьИнформациюОПланеИдПлана(идПлана: int): map<string, any>
    """
    __tablename__ = "catalog"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)  # furniture, materials, fixtures
    
    items_count = Column(Integer, default=0)
    
    # Метаданные
    metadata = Column(JSON)

    def __repr__(self):
        return f"<Catalog {self.name}>"
