"""
Валидатор из диаграммы классов

Класс: Валидатор
Attributes:
    - параметры: list<string>
    - стандарты: Стандарт

Methods:
    - соответствуетСтандарту(модель: Модель): bool
    - проверитьПараметры(параметры: list<string>): list<string>
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Tuple
import logging

from ..models.model import Model
from ..models.room import Room
from ..models.catalog import Standard
from ..models.project import Project

logger = logging.getLogger(__name__)


class ValidationResult:
    """Результат валидации"""
    def __init__(self, is_valid: bool, errors: List[str], warnings: List[str]):
        self.is_valid = is_valid
        self.errors = errors
        self.warnings = warnings
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }


class Validator:
    """
    Валидатор для проверки соответствия моделей и планировок стандартам
    Реализует проверку:
    - Строительных норм (СНиП)
    - Эргономических требований
    - Безопасности конструкций
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.standards = self._load_standards()
    
    def _load_standards(self) -> List[Standard]:
        """Загрузка стандартов из БД"""
        return self.db.query(Standard).all()
    
    def validate_model(self, model: Model) -> ValidationResult:
        """
        соответствуетСтандарту(модель: Модель): bool
        Проверяет соответствие модели стандартам
        """
        errors = []
        warnings = []
        
        # Проверка размеров модели
        if model.dimensions:
            dim_errors, dim_warnings = self._check_dimensions(model.dimensions, model.type)
            errors.extend(dim_errors)
            warnings.extend(dim_warnings)
        else:
            warnings.append(f"Модель {model.name}: отсутствуют размеры")
        
        # Проверка позиции (не должна быть вне комнаты)
        if model.room_id:
            room_errors = self._check_model_position(model)
            errors.extend(room_errors)
        
        # Проверка материала на соответствие стандартам
        if model.material_id:
            material_errors = self._check_material_standards(model.material_id)
            errors.extend(material_errors)
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)
    
    def validate_room(self, room: Room) -> ValidationResult:
        """
        Проверяет помещение на соответствие строительным нормам
        """
        errors = []
        warnings = []
        
        # Проверка минимальной высоты потолков (СНиП)
        if room.height < 2.5:
            errors.append(f"Комната {room.name}: высота потолка {room.height}м меньше минимальной (2.5м)")
        elif room.height < 2.7:
            warnings.append(f"Комната {room.name}: рекомендуется высота потолка не менее 2.7м")
        
        # Проверка площади
        if room.area and room.area < 8:
            warnings.append(f"Комната {room.name}: площадь {room.area}м² меньше рекомендуемой для жилых помещений")
        
        # Проверка пропорций
        if room.width and room.length:
            ratio = max(room.width, room.length) / min(room.width, room.length)
            if ratio > 3:
                warnings.append(f"Комната {room.name}: неоптимальные пропорции (соотношение {ratio:.1f}:1)")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)
    
    def validate_project(self, project_id: int) -> ValidationResult:
        """
        проверитьПараметры(параметры: list<string>): list<string>
        Проверяет весь проект на соответствие стандартам
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return ValidationResult(False, ["Проект не найден"], [])
        
        all_errors = []
        all_warnings = []
        
        # Проверка всех комнат
        rooms = self.db.query(Room).filter(Room.project_id == project_id).all()
        for room in rooms:
            result = self.validate_room(room)
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
        
        # Проверка всех моделей
        models = self.db.query(Model).filter(Model.project_id == project_id).all()
        for model in models:
            result = self.validate_model(model)
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
        
        # Проверка общей площади проекта
        total_area = sum(r.area or 0 for r in rooms)
        if total_area < 20:
            warnings.append(f"Общая площадь проекта ({total_area}м²) меньше минимальной для квартиры")
        
        is_valid = len(all_errors) == 0
        return ValidationResult(is_valid, all_errors, all_warnings)
    
    def _check_dimensions(
        self,
        dimensions: Dict[str, float],
        model_type: str
    ) -> Tuple[List[str], List[str]]:
        """Проверка размеров объекта"""
        errors = []
        warnings = []
        
        # Базовые проверки
        for dim_name, value in dimensions.items():
            if value <= 0:
                errors.append(f"Недопустимый размер {dim_name}: {value}")
        
        # Специфические проверки для типов мебели
        if model_type == "furniture":
            # Проверка на слишком большую мебель
            max_dim = max(dimensions.values()) if dimensions else 0
            if max_dim > 5:
                warnings.append(f"Необычно большой размер мебели: {max_dim}м")
        
        return errors, warnings
    
    def _check_model_position(self, model: Model) -> List[str]:
        """Проверка, что модель находится в пределах комнаты"""
        errors = []
        
        room = self.db.query(Room).filter(Room.id == model.room_id).first()
        if not room or not model.position:
            return errors
        
        # Проверка координат
        pos = model.position
        if "x" in pos and "z" in pos:
            if pos["x"] < 0 or pos["x"] > room.width:
                errors.append(f"Модель {model.name} выходит за границы комнаты по X")
            if pos["z"] < 0 or pos["z"] > room.length:
                errors.append(f"Модель {model.name} выходит за границы комнаты по Z")
        
        return errors
    
    def _check_material_standards(self, material_id: int) -> List[str]:
        """Проверка материала на соответствие стандартам"""
        errors = []
        
        # Получаем стандарты для материала
        standards = self.db.query(Standard).filter(
            Standard.material_id == material_id
        ).all()
        
        if not standards:
            errors.append(f"Для материала ID {material_id} не найдены стандарты")
        
        # TODO: Более детальная проверка параметров материала
        
        return errors
