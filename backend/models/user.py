from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..database import Base


class UserRole(str, enum.Enum):
    """Роли пользователей согласно диаграмме"""
    CLIENT = "client"  # Клиент
    DESIGNER = "designer"  # Дизайнер
    MANAGER = "manager"  # Менеджер
    CONSULTANT = "consultant"  # Консультант


class User(Base):
    """
    Модель Пользователь из диаграммы классов
    Attributes:
        - идПользователя: int
        - полноеИмя: string
        - email: string
        - пароль: string
        - роль: string (Клиент/Дизайнер/Менеджер)
    Methods:
        - войти(логин, пароль): void
        - редактироватьПрофиль(данные): void
        - просмотретьБронированиеПроектов(): Проект
        - добавитьКомментарий(проект, текст): void
        - создатьЗапросНаКонсультацию(дизайнер, текст): void
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CLIENT)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    projects = relationship("Project", back_populates="user", foreign_keys="Project.user_id")
    assigned_projects = relationship("Project", back_populates="designer", foreign_keys="Project.designer_id")
    comments = relationship("Comment", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="sender")
    consultations = relationship("Consultation", back_populates="client")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
