from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..database import get_db
from ..models.user import User
from ..models.project import Project
from ..models.room import Room
from ..models.model import Model
from ..services.validator import Validator
from .auth import get_current_user

router = APIRouter()


@router.post("/project/{project_id}")
def validate_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Валидация проекта на соответствие стандартам
    Реализует: проверитьПараметры(параметры: list<string>)
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Проверка прав
    if (project.user_id != current_user.id and 
        project.designer_id != current_user.id and
        current_user.role not in ["manager", "consultant"]):
        raise HTTPException(status_code=403, detail="Нет доступа")
    
    validator = Validator(db)
    result = validator.validate_project(project_id)
    
    return result.to_dict()


@router.post("/room/{room_id}")
def validate_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Валидация комнаты"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")
    
    validator = Validator(db)
    result = validator.validate_room(room)
    
    return result.to_dict()


@router.post("/model/{model_id}")
def validate_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Валидация модели на соответствие стандартам
    Реализует: соответствуетСтандарту(модель: Модель)
    """
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Модель не найдена")
    
    validator = Validator(db)
    result = validator.validate_model(model)
    
    return result.to_dict()
