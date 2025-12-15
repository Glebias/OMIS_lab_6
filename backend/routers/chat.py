from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime

from ..database import get_db
from ..models.user import User
from ..models.chat import ChatMessage, Consultation, Comment
from ..models.project import Project
from ..schemas.chat import (
    ChatMessageCreate, ChatMessageResponse,
    ConsultationCreate, ConsultationUpdate, ConsultationResponse,
    CommentCreate, CommentResponse
)
from .auth import get_current_user

router = APIRouter()


# ============= СООБЩЕНИЯ ЧАТА =============

@router.post("/messages", response_model=ChatMessageResponse, status_code=201)
def send_message(
    message: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Отправить сообщение в чат
    Реализация из диаграммы: показатьСообщения(чат: Чат)
    """
    # Проверка получателя
    if message.recipient_id:
        recipient = db.query(User).filter(User.id == message.recipient_id).first()
        if not recipient:
            raise HTTPException(status_code=404, detail="Получатель не найден")
    
    # Проверка проекта
    if message.project_id:
        project = db.query(Project).filter(Project.id == message.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден")
        
        # Проверка прав доступа к проекту
        if (project.user_id != current_user.id and 
            project.designer_id != current_user.id and
            current_user.role not in ["manager", "consultant"]):
            raise HTTPException(status_code=403, detail="Нет доступа к проекту")
    
    db_message = ChatMessage(
        sender_id=current_user.id,
        recipient_id=message.recipient_id,
        project_id=message.project_id,
        message=message.message
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    return db_message


@router.get("/messages", response_model=List[ChatMessageResponse])
def get_messages(
    recipient_id: int = None,
    project_id: int = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить сообщения чата
    выделитьСрочные(): void
    """
    query = db.query(ChatMessage)
    
    # Фильтрация по получателю или отправителю
    if recipient_id:
        query = query.filter(
            ((ChatMessage.sender_id == current_user.id) & (ChatMessage.recipient_id == recipient_id)) |
            ((ChatMessage.sender_id == recipient_id) & (ChatMessage.recipient_id == current_user.id))
        )
    else:
        # Все сообщения пользователя
        query = query.filter(
            (ChatMessage.sender_id == current_user.id) | 
            (ChatMessage.recipient_id == current_user.id)
        )
    
    # Фильтрация по проекту
    if project_id:
        query = query.filter(ChatMessage.project_id == project_id)
    
    messages = query.order_by(ChatMessage.created_at.desc()).offset(skip).limit(limit).all()
    return messages


@router.put("/messages/{message_id}/read")
def mark_message_as_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Пометить сообщение как прочитанное"""
    message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    
    # Только получатель может пометить как прочитанное
    if message.recipient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    
    message.is_read = True
    db.commit()
    
    return {"message": "Сообщение помечено как прочитанное"}


@router.get("/messages/unread/count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить количество непрочитанных сообщений"""
    count = db.query(ChatMessage).filter(
        ChatMessage.recipient_id == current_user.id,
        ChatMessage.is_read == False
    ).count()
    
    return {"unread_count": count}


# ============= КОНСУЛЬТАЦИИ =============

@router.post("/consultations", response_model=ConsultationResponse, status_code=201)
def create_consultation(
    consultation: ConsultationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создать запрос на консультацию
    Реализует: создатьЗапросНаКонсультацию(дизайнер, текст)
    """
    # Проверка проекта если указан
    if consultation.project_id:
        project = db.query(Project).filter(Project.id == consultation.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден")
        
        if project.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Нет доступа к проекту")
    
    db_consultation = Consultation(
        client_id=current_user.id,
        topic=consultation.topic,
        description=consultation.description,
        project_id=consultation.project_id
    )
    db.add(db_consultation)
    db.commit()
    db.refresh(db_consultation)
    
    return db_consultation


@router.get("/consultations", response_model=List[ConsultationResponse])
def get_consultations(
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить консультации"""
    query = db.query(Consultation)
    
    # Фильтрация по роли
    if current_user.role == "client":
        # Клиент видит только свои запросы
        query = query.filter(Consultation.client_id == current_user.id)
    elif current_user.role in ["designer", "consultant"]:
        # Консультанты видят назначенные им или pending
        query = query.filter(
            (Consultation.consultant_id == current_user.id) |
            (Consultation.status == "pending")
        )
    # Менеджеры видят все
    
    if status:
        query = query.filter(Consultation.status == status)
    
    consultations = query.order_by(Consultation.created_at.desc()).offset(skip).limit(limit).all()
    return consultations


@router.get("/consultations/{consultation_id}", response_model=ConsultationResponse)
def get_consultation(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить консультацию по ID"""
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(status_code=404, detail="Консультация не найдена")
    
    # Проверка прав доступа
    if (consultation.client_id != current_user.id and
        consultation.consultant_id != current_user.id and
        current_user.role not in ["manager"]):
        raise HTTPException(status_code=403, detail="Нет доступа")
    
    return consultation


@router.put("/consultations/{consultation_id}", response_model=ConsultationResponse)
def update_consultation(
    consultation_id: int,
    consultation_update: ConsultationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновить консультацию (назначить консультанта, изменить статус)
    """
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(status_code=404, detail="Консультация не найдена")
    
    # Проверка прав
    if current_user.role not in ["designer", "consultant", "manager"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Назначение консультанта
    if consultation_update.consultant_id:
        consultant = db.query(User).filter(User.id == consultation_update.consultant_id).first()
        if not consultant or consultant.role not in ["designer", "consultant"]:
            raise HTTPException(status_code=400, detail="Неверный консультант")
        consultation.consultant_id = consultation_update.consultant_id
        consultation.status = "assigned"
    
    # Обновление других полей
    for key, value in consultation_update.dict(exclude_unset=True, exclude={"consultant_id"}).items():
        setattr(consultation, key, value)
    
    # Установка времени завершения
    if consultation_update.status == "completed" and not consultation.completed_at:
        consultation.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(consultation)
    return consultation


@router.post("/consultations/{consultation_id}/assign")
def assign_consultation_to_self(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Назначить консультацию на себя (для дизайнеров/консультантов)"""
    if current_user.role not in ["designer", "consultant"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(status_code=404, detail="Консультация не найдена")
    
    if consultation.consultant_id:
        raise HTTPException(status_code=400, detail="Консультация уже назначена")
    
    consultation.consultant_id = current_user.id
    consultation.status = "assigned"
    db.commit()
    
    return {"message": "Консультация назначена"}


# ============= КОММЕНТАРИИ =============

@router.post("/comments", response_model=CommentResponse, status_code=201)
def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Добавить комментарий к проекту
    Реализует: добавитьКомментарий(проект, текст)
    """
    project = db.query(Project).filter(Project.id == comment.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Проверка прав доступа
    if (project.user_id != current_user.id and 
        project.designer_id != current_user.id and
        current_user.role not in ["manager", "consultant"]):
        raise HTTPException(status_code=403, detail="Нет доступа к проекту")
    
    db_comment = Comment(
        user_id=current_user.id,
        project_id=comment.project_id,
        text=comment.text
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    return db_comment


@router.get("/comments/project/{project_id}", response_model=List[CommentResponse])
def get_project_comments(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить все комментарии проекта"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Проверка прав доступа
    if (project.user_id != current_user.id and 
        project.designer_id != current_user.id and
        current_user.role not in ["manager", "consultant"]):
        raise HTTPException(status_code=403, detail="Нет доступа")
    
    comments = db.query(Comment).filter(
        Comment.project_id == project_id
    ).order_by(Comment.created_at.desc()).offset(skip).limit(limit).all()
    
    return comments


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить комментарий"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    
    # Только автор или менеджер может удалить
    if comment.user_id != current_user.id and current_user.role != "manager":
        raise HTTPException(status_code=403, detail="Нет прав на удаление")
    
    db.delete(comment)
    db.commit()
    return {"message": "Комментарий удален"}


# ============= WebSocket для реального времени =============

class ConnectionManager:
    """Менеджер WebSocket соединений для чата в реальном времени"""
    
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """
    WebSocket endpoint для чата в реальном времени
    Использование:
    ws://localhost:8000/api/chat/ws/{user_id}
    """
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Ожидаем сообщения от клиента
            data = await websocket.receive_text()
            # Здесь можно обрабатывать входящие сообщения
            # и отправлять их другим пользователям
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
