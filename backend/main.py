from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import engine, Base
from .routers import (
    auth,
    users,
    projects,
    rooms,
    models,
    catalog,
    recommendations,
    chat,
    analysis,
    validator,
    corrector
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создание таблиц при запуске
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Платформа для виртуального интерьерного дизайна",
    description="Backend API для системы дизайна интерьеров с 3D моделированием",
    version="1.0.0",
    lifespan=lifespan
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router, prefix="/api/auth", tags=["Авторизация"])
app.include_router(users.router, prefix="/api/users", tags=["Пользователи"])
app.include_router(projects.router, prefix="/api/projects", tags=["Проекты"])
app.include_router(rooms.router, prefix="/api/rooms", tags=["Помещения"])
app.include_router(models.router, prefix="/api/models", tags=["3D Модели"])
app.include_router(catalog.router, prefix="/api/catalog", tags=["Каталог"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Рекомендации"])
app.include_router(chat.router, prefix="/api/chat", tags=["Чат"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Анализ"])
app.include_router(validator.router, prefix="/api/validator", tags=["Валидатор"])
app.include_router(corrector.router, prefix="/api/corrector", tags=["Корректор"])


@app.get("/")
async def root():
    return {"message": "Interior Design Platform API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
