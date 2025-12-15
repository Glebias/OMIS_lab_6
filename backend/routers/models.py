from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User
from ..models.model import Model
from ..models.room import Room
from ..schemas.model import ModelCreate, ModelUpdate, ModelResponse
from .auth import get_current_user

router = APIRouter()


@router.post("/", response_model=ModelResponse, status_code=201)
def create_model(
    model: ModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Добавить 3D модель в проект/комнату"""
    # Проверка прав доступа к комнате/проекту
    if model.room_id:
        room = db.query(Room).filter(Room.id == model.room_id).first()
        if not room:
            raise HTTPException(status_code=404, detail="Комната не найдена")
        project = room.project
    elif model.project_id:
        from ..models.project import Project
        project = db.query(Project).filter(Project.id == model.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден")
    else:
        raise HTTPException(status_code=400, detail="Укажите project_id или room_id")
    
    if (project.user_id != current_user.id and 
        project.designer_id != current_user.id and
        current_user.role not in ["manager"]):
        raise HTTPException(status_code=403, detail="Нет доступа к этому проекту")
    
    db_model = Model(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


@router.get("/room/{room_id}", response_model=List[ModelResponse])
def get_room_models(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить все модели в комнате"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")
    
    project = room.project
    if (project.user_id != current_user.id and 
        project.designer_id != current_user.id and
        current_user.role not in ["manager", "consultant"]):
        raise HTTPException(status_code=403, detail="Нет доступа")
    
    models = db.query(Model).filter(Model.room_id == room_id).all()
    return models


@router.put("/{model_id}", response_model=ModelResponse)
def update_model(
    model_id: int,
    model_update: ModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить модель (позиция, материал, и т.д.)"""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Модель не найдена")
    
    # Проверка прав через проект
    if model.room_id:
        room = db.query(Room).filter(Room.id == model.room_id).first()
        project = room.project
    else:
        from ..models.project import Project
        project = db.query(Project).filter(Project.id == model.project_id).first()
    
    if (project.user_id != current_user.id and 
        project.designer_id != current_user.id and
        current_user.role != "manager"):
        raise HTTPException(status_code=403, detail="Нет доступа")
    
    for key, value in model_update.dict(exclude_unset=True).items():
        setattr(model, key, value)
    
    db.commit()
    db.refresh(model)
    return model


@router.delete("/{model_id}")
def delete_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить модель"""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Модель не найдена")
    
    db.delete(model)
    db.commit()
    return {"message": "Модель удалена"}
