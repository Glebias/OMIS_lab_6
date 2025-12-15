from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models.user import User
from ..models.catalog import Material, Standard, Catalog
from ..schemas.catalog import (
    MaterialCreate, MaterialUpdate, MaterialResponse,
    StandardCreate, StandardUpdate, StandardResponse,
    CatalogCreate, CatalogUpdate, CatalogResponse
)
from .auth import get_current_user

router = APIRouter()


# ============= МАТЕРИАЛЫ =============

@router.post("/materials", response_model=MaterialResponse, status_code=201)
def create_material(
    material: MaterialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создать новый материал (только дизайнер или менеджер)
    """
    if current_user.role not in ["designer", "manager"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    db_material = Material(**material.dict())
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material


@router.get("/materials", response_model=List[MaterialResponse])
def get_materials(
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = Query(None, description="Фильтр по типу материала"),
    search: Optional[str] = Query(None, description="Поиск по названию"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список всех материалов с фильтрацией
    Реализация метода из диаграммы: фильтроватьМатериалы(критерии)
    """
    query = db.query(Material)
    
    if type:
        query = query.filter(Material.type == type)
    
    if search:
        query = query.filter(Material.name.contains(search))
    
    materials = query.offset(skip).limit(limit).all()
    return materials


@router.get("/materials/{material_id}", response_model=MaterialResponse)
def get_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить материал по ID"""
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Материал не найден")
    return material


@router.put("/materials/{material_id}", response_model=MaterialResponse)
def update_material(
    material_id: int,
    material_update: MaterialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить материал"""
    if current_user.role not in ["designer", "manager"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Материал не найден")
    
    for key, value in material_update.dict(exclude_unset=True).items():
        setattr(material, key, value)
    
    db.commit()
    db.refresh(material)
    return material


@router.delete("/materials/{material_id}")
def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить материал"""
    if current_user.role != "manager":
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Материал не найден")
    
    db.delete(material)
    db.commit()
    return {"message": "Материал удален"}


# ============= СТАНДАРТЫ =============

@router.post("/standards", response_model=StandardResponse, status_code=201)
def create_standard(
    standard: StandardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создать новый стандарт (СНиП, ГОСТ и т.д.)
    """
    if current_user.role not in ["designer", "manager"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Проверка уникальности кода
    existing = db.query(Standard).filter(Standard.code == standard.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Стандарт с таким кодом уже существует")
    
    db_standard = Standard(**standard.dict())
    db.add(db_standard)
    db.commit()
    db.refresh(db_standard)
    return db_standard


@router.get("/standards", response_model=List[StandardResponse])
def get_standards(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = Query(None, description="Категория стандарта"),
    search: Optional[str] = Query(None, description="Поиск по названию или коду"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список стандартов с фильтрацией
    Реализация: найтиСтандартДляПланировки(критерии)
    """
    query = db.query(Standard)
    
    if category:
        query = query.filter(Standard.category == category)
    
    if search:
        query = query.filter(
            (Standard.name.contains(search)) | (Standard.code.contains(search))
        )
    
    standards = query.offset(skip).limit(limit).all()
    return standards


@router.get("/standards/{standard_id}", response_model=StandardResponse)
def get_standard(
    standard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить стандарт по ID"""
    standard = db.query(Standard).filter(Standard.id == standard_id).first()
    if not standard:
        raise HTTPException(status_code=404, detail="Стандарт не найден")
    return standard


@router.put("/standards/{standard_id}", response_model=StandardResponse)
def update_standard(
    standard_id: int,
    standard_update: StandardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить стандарт"""
    if current_user.role not in ["designer", "manager"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    standard = db.query(Standard).filter(Standard.id == standard_id).first()
    if not standard:
        raise HTTPException(status_code=404, detail="Стандарт не найден")
    
    for key, value in standard_update.dict(exclude_unset=True).items():
        setattr(standard, key, value)
    
    db.commit()
    db.refresh(standard)
    return standard


# ============= КАТАЛОГ =============

@router.post("/", response_model=CatalogResponse, status_code=201)
def create_catalog(
    catalog: CatalogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать каталог"""
    if current_user.role not in ["designer", "manager"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    db_catalog = Catalog(**catalog.dict())
    db.add(db_catalog)
    db.commit()
    db.refresh(db_catalog)
    return db_catalog


@router.get("/", response_model=List[CatalogResponse])
def get_catalogs(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = Query(None, description="Категория каталога"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список каталогов
    Реализация: получитьИнформациюОПланеИдПлана(идПлана: int)
    """
    query = db.query(Catalog)
    
    if category:
        query = query.filter(Catalog.category == category)
    
    catalogs = query.offset(skip).limit(limit).all()
    return catalogs


@router.get("/{catalog_id}", response_model=CatalogResponse)
def get_catalog(
    catalog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить каталог по ID
    Реализация метода из диаграммы: получитьИнформациюОПланеИдПлана
    """
    catalog = db.query(Catalog).filter(Catalog.id == catalog_id).first()
    if not catalog:
        raise HTTPException(status_code=404, detail="Каталог не найден")
    return catalog


@router.get("/{catalog_id}/stats")
def get_catalog_stats(
    catalog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить статистику каталога
    Возвращает общую информацию как map<string, any>
    """
    catalog = db.query(Catalog).filter(Catalog.id == catalog_id).first()
    if not catalog:
        raise HTTPException(status_code=404, detail="Каталог не найден")
    
    # Подсчет статистики
    materials_count = db.query(Material).count()
    standards_count = db.query(Standard).count()
    
    return {
        "catalog_id": catalog.id,
        "catalog_name": catalog.name,
        "category": catalog.category,
        "items_count": catalog.items_count,
        "total_materials": materials_count,
        "total_standards": standards_count,
        "metadata": catalog.metadata
    }
