from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User
from ..models.project import Project
from ..schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectWithRooms
from .auth import get_current_user

router = APIRouter()


@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать новый проект"""
    db_project = Project(
        name=project.name,
        description=project.description,
        status=project.status,
        user_id=current_user.id,
        designer_id=project.designer_id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("/", response_model=List[ProjectResponse])
def get_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список проектов текущего пользователя"""
    # Если пользователь - дизайнер или менеджер, показываем все проекты
    if current_user.role in ["designer", "manager", "consultant"]:
        projects = db.query(Project).offset(skip).limit(limit).all()
    else:
        projects = db.query(Project).filter(
            Project.user_id == current_user.id
        ).offset(skip).limit(limit).all()
    
    return projects


@router.get("/{project_id}", response_model=ProjectWithRooms)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить проект по ID с комнатами"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Проверка прав доступа
    if (project.user_id != current_user.id and 
        project.designer_id != current_user.id and
        current_user.role not in ["manager", "consultant"]):
        raise HTTPException(status_code=403, detail="Нет доступа к этому проекту")
    
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить проект"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Проверка прав
    if (project.user_id != current_user.id and 
        project.designer_id != current_user.id and
        current_user.role != "manager"):
        raise HTTPException(status_code=403, detail="Нет доступа к этому проекту")
    
    for key, value in project_update.dict(exclude_unset=True).items():
        setattr(project, key, value)
    
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить проект"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Только владелец или менеджер могут удалить
    if project.user_id != current_user.id and current_user.role != "manager":
        raise HTTPException(status_code=403, detail="Нет прав на удаление")
    
    db.delete(project)
    db.commit()
    return {"message": "Проект удален"}
