from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User
from ..models.project import Project
from ..models.room import Room
from ..schemas.room import RoomCreate, RoomUpdate, RoomResponse
from .auth import get_current_user

router = APIRouter()


@router.post("/", response_model=RoomResponse, status_code=201)
def create_room(
    room: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать комнату в проекте"""
    # Проверка существования проекта и прав доступа
    project = db.query(Project).filter(Project.id == room.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    if (project.user_id != current_user.id and 
        project.designer_id != current_user.id and
        current_user.role not in ["manager"]):
        raise HTTPException(status_code=403, detail="Нет доступа к этому проекту")
    
    # Вычисление площади
    area = room.width * room.length
    
    db_room = Room(
        name=room.name,
        width=room.width,
        length=room.length,
        height=room.height,
        area=area,
        project_id=room.project_id,
        position=room.position,
        rotation=room.rotation
    )
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


@router.get("/project/{project_id}", response_model=List[RoomResponse])
def get_project_rooms(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить все комнаты проекта"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    if (project.user_id != current_user.id and 
        project.designer_id != current_user.id and
        current_user.role not in ["manager", "consultant"]):
        raise HTTPException(status_code=403, detail="Нет доступа к этому проекту")
    
    rooms = db.query(Room).filter(Room.project_id == project_id).all()
    return rooms


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить комнату по ID"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")
    
    # Проверка прав через проект
    project = room.project
    if (project.user_id != current_user.id and 
        project.designer_id != current_user.id and
        current_user.role not in ["manager", "consultant"]):
        raise HTTPException(status_code=403, detail="Нет доступа")
    
    return room


@router.put("/{room_id}", response_model=RoomResponse)
def update_room(
    room_id: int,
    room_update: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить комнату"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")
    
    project = room.project
    if (project.user_id != current_user.id and 
        project.designer_id != current_user.id and
        current_user.role != "manager"):
        raise HTTPException(status_code=403, detail="Нет доступа")
    
    for key, value in room_update.dict(exclude_unset=True).items():
        setattr(room, key, value)
    
    # Пересчет площади если изменились размеры
    if room_update.width or room_update.length:
        room.area = room.width * room.length
    
    db.commit()
    db.refresh(room)
    return room


@router.delete("/{room_id}")
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить комнату"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")
    
    project = room.project
    if (project.user_id != current_user.id and 
        project.designer_id != current_user.id and
        current_user.role != "manager"):
        raise HTTPException(status_code=403, detail="Нет прав на удаление")
    
    db.delete(room)
    db.commit()
    return {"message": "Комната удалена"}
