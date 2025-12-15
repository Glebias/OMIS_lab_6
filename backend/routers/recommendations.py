from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User
from ..models.recommendation import Recommendation, Task
from ..models.project import Project
from ..schemas.recommendation import (
    RecommendationCreate, RecommendationUpdate, RecommendationResponse,
    TaskCreate, TaskUpdate, TaskResponse
)
from ..services.recommendation_system import RecommendationSystem
from .auth import get_current_user

router = APIRouter()


# ============= РЕКОМЕНДАЦИИ =============

@router.post("/", response_model=RecommendationResponse, status_code=201)
def create_recommendation(
    recommendation: RecommendationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создать рекомендацию вручную
    """
    if current_user.role not in ["designer", "manager", "consultant"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Проверка существования проекта
    project = db.query(Project).filter(Project.id == recommendation.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    db_recommendation = Recommendation(**recommendation.dict())
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation


@router.post("/generate/{project_id}", response_model=List[RecommendationResponse])
def generate_recommendations(
    project_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Сгенерировать AI-рекомендации для проекта
    Реализация метода: предложитьАльтернативы(проект: Проект)
    
    ⚠️ Использует заглушки. Интегрируйте LLM для реальной генерации.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Проверка прав доступа
    if (project.user_id != current_user.id and 
        project.designer_id != current_user.id and
        current_user.role not in ["manager", "consultant"]):
        raise HTTPException(status_code=403, detail="Нет доступа к проекту")
    
    # Генерация рекомендаций
    rec_system = RecommendationSystem(db)
    recommendations = rec_system.suggest_alternatives(project)
    
    return recommendations


@router.get("/project/{project_id}", response_model=List[RecommendationResponse])
def get_project_recommendations(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить все рекомендации для проекта"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    if (project.user_id != current_user.id and 
        project.designer_id != current_user.id and
        current_user.role not in ["manager", "consultant"]):
        raise HTTPException(status_code=403, detail="Нет доступа")
    
    recommendations = db.query(Recommendation).filter(
        Recommendation.project_id == project_id
    ).all()
    
    return recommendations


@router.put("/{recommendation_id}", response_model=RecommendationResponse)
def update_recommendation(
    recommendation_id: int,
    recommendation_update: RecommendationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить рекомендацию (например, пометить как примененную)"""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id
    ).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Рекомендация не найдена")
    
    for key, value in recommendation_update.dict(exclude_unset=True).items():
        setattr(recommendation, key, value)
    
    db.commit()
    db.refresh(recommendation)
    return recommendation


@router.delete("/{recommendation_id}")
def delete_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить рекомендацию"""
    if current_user.role not in ["designer", "manager"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id
    ).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Рекомендация не найдена")
    
    db.delete(recommendation)
    db.commit()
    return {"message": "Рекомендация удалена"}


# ============= ЗАДАНИЯ =============

@router.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать задание (Задание из диаграммы)"""
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("/tasks/room/{room_id}", response_model=List[TaskResponse])
def get_room_tasks(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить все задания для комнаты"""
    tasks = db.query(Task).filter(Task.room_id == room_id).all()
    return tasks


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить задание"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    
    for key, value in task_update.dict(exclude_unset=True).items():
        setattr(task, key, value)
    
    # Если статус changed to completed, установить completed_at
    if task_update.status == "completed" and not task.completed_at:
        from datetime import datetime
        task.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(task)
    return task
