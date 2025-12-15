from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ..database import get_db
from ..models.user import User
from ..models.project import Project
from ..models.analysis import AnalysisResult
from ..services.recommendation_system import RecommendationSystem
from .auth import get_current_user

router = APIRouter()


@router.post("/project/{project_id}")
def analyze_project(
    project_id: int,
    analysis_type: str = "layout",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Анализировать проект
    
    Типы анализа:
    - layout: анализ планировки
    - lighting: анализ освещения
    - ergonomics: эргономика пространства
    - cost: стоимостной анализ
    
    ⚠️ Использует заглушки. Для полного анализа интегрируйте LLM.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Проверка прав
    if (project.user_id != current_user.id and 
        project.designer_id != current_user.id and
        current_user.role not in ["manager", "consultant"]):
        raise HTTPException(status_code=403, detail="Нет доступа")
    
    # Выполняем анализ
    rec_system = RecommendationSystem(db)
    analysis_result = rec_system.analyze_project_layout(project_id)
    
    # Сохраняем результат в БД
    db_analysis = AnalysisResult(
        project_id=project_id,
        analysis_type=analysis_type,
        score=analysis_result["analysis"]["score"],
        status="good" if analysis_result["analysis"]["score"] > 75 else "warning",
        details=analysis_result,
        issues=analysis_result["analysis"]["issues"],
        suggestions=analysis_result["analysis"]["suggestions"],
        report=f"Анализ проекта #{project_id}: Общая оценка {analysis_result['analysis']['score']}/100"
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    
    return analysis_result


@router.get("/project/{project_id}/results")
def get_project_analysis_results(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[AnalysisResult]:
    """Получить все результаты анализа проекта"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    if (project.user_id != current_user.id and 
        project.designer_id != current_user.id and
        current_user.role not in ["manager", "consultant"]):
        raise HTTPException(status_code=403, detail="Нет доступа")
    
    results = db.query(AnalysisResult).filter(
        AnalysisResult.project_id == project_id
    ).all()
    
    return results
