"""
Сервис для работы с каталогом
Реализует бизнес-логику из диаграммы классов
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from ..models.catalog import Material, Standard, Catalog
from ..models.model import Model


class CatalogService:
    """
    Класс Каталог из диаграммы
    Методы:
        - получитьИнформациюОПланеИдПлана(идПлана: int): map<string, any>
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_plan_info(self, plan_id: int) -> Dict[str, Any]:
        """
        получитьИнформациюОПланеИдПлана(идПлана: int): map<string, any>
        Получить информацию о плане/проекте по ID
        """
        from ..models.project import Project
        from ..models.room import Room
        
        project = self.db.query(Project).filter(Project.id == plan_id).first()
        if not project:
            return None
        
        # Собираем информацию о проекте
        rooms = self.db.query(Room).filter(Room.project_id == plan_id).all()
        models = self.db.query(Model).filter(Model.project_id == plan_id).all()
        
        total_area = sum(room.area for room in rooms if room.area)
        
        return {
            "project_id": project.id,
            "project_name": project.name,
            "description": project.description,
            "status": project.status,
            "rooms_count": len(rooms),
            "total_area": total_area,
            "models_count": len(models),
            "created_at": project.created_at.isoformat(),
            "rooms": [
                {
                    "id": room.id,
                    "name": room.name,
                    "area": room.area,
                    "dimensions": {
                        "width": room.width,
                        "length": room.length,
                        "height": room.height
                    }
                }
                for room in rooms
            ],
            "models": [
                {
                    "id": model.id,
                    "name": model.name,
                    "type": model.type,
                    "category": model.category
                }
                for model in models
            ]
        }
    
    def filter_materials(
        self,
        criteria: Dict[str, Any]
    ) -> List[Material]:
        """
        фильтроватьМатериалы(критерии: map<string, string>): list<Материал>
        Фильтрация материалов по критериям
        """
        query = self.db.query(Material)
        
        if "type" in criteria:
            query = query.filter(Material.type == criteria["type"])
        
        if "name" in criteria:
            query = query.filter(Material.name.contains(criteria["name"]))
        
        if "properties" in criteria:
            # Фильтрация по свойствам материала
            for key, value in criteria["properties"].items():
                query = query.filter(
                    Material.properties[key].astext == str(value)
                )
        
        return query.all()
    
    def find_standard(
        self,
        plan_id: int,
        criteria: Optional[Dict[str, Any]] = None
    ) -> List[Standard]:
        """
        найтиСтандартДляПланировки(критерии: Стандарт): list<Стандарт>
        Найти подходящие стандарты для планировки
        """
        query = self.db.query(Standard)
        
        if criteria:
            if "category" in criteria:
                query = query.filter(Standard.category == criteria["category"])
            
            if "code" in criteria:
                query = query.filter(Standard.code.contains(criteria["code"]))
        
        return query.all()
    
    def get_material_with_standards(
        self,
        material_id: int
    ) -> Dict[str, Any]:
        """
        Получить материал со связанными стандартами
        """
        material = self.db.query(Material).filter(Material.id == material_id).first()
        if not material:
            return None
        
        standards = self.db.query(Standard).filter(
            Standard.material_id == material_id
        ).all()
        
        return {
            "material": {
                "id": material.id,
                "name": material.name,
                "type": material.type,
                "texture_url": material.texture_url,
                "properties": material.properties
            },
            "standards": [
                {
                    "id": std.id,
                    "name": std.name,
                    "code": std.code,
                    "category": std.category,
                    "parameters": std.parameters
                }
                for std in standards
            ]
        }
