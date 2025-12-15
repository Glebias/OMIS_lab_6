from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..database import get_db
from ..models.user import User
from ..models.project import Project
from ..models.room import Room
from ..models.model import Model
from ..services.corrector import Corrector
from .auth import get_current_user

router = APIRouter()


@router.post("/model/{model_id}/optimize")
def optimize_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Оптимизация модели
    Реализует: оптимизироватьМодель(модели: Модель)
    """
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Модель не найдена")
    
    # Проверка прав через проект
    if model.project_id:
        project = db.query(Project).filter(Project.id == model.project_id).first()
        if (project.user_id != current_user.id and 
            project.designer_id != current_user.id and
            current_user.role not in ["manager"]):
            raise HTTPException(status_code=403, detail="Нет доступа")
    
    corrector = Corrector(db)
    result = corrector.optimize_model(model)
    
    return result.to_dict()


@router.post("/room/{room_id}/optimize")
def optimize_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Оптимизация всех моделей в комнате"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")
    
    project = room.project
    if (project.user_id != current_user.id and 
        project.designer_id != current_user.id and
        current_user.role not in ["manager"]):
        raise HTTPException(status_code=403, detail="Нет доступа")
    
    corrector = Corrector(db)
    result = corrector.optimize_room_layout(room_id)
    
    return result.to_dict()


@router.post("/project/{project_id}/optimize")
def optimize_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Оптимизация всего проекта"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    if (project.user_id != current_user.id and 
        project.designer_id != current_user.id and
        current_user.role not in ["manager"]):
        raise HTTPException(status_code=403, detail="Нет доступа")
    
    corrector = Corrector(db)
    result = corrector.optimize_project(project_id)
    
    return result.to_dict()
