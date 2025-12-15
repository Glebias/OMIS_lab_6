# Backend Project Overview

This backend project is designed to support a system for managing interior design projects. It provides functionality for user authentication, project management, chat, and 3D modeling. Below is a detailed overview of the project structure, key features, and the implementation of the object model.

## Project Structure

The backend is organized into the following main components:

1. **Database (`database.py`)**:
   - Configures the SQLAlchemy ORM for database interactions.
   - Defines the base model for all database tables.

2. **Models (`models/`)**:
   - Contains SQLAlchemy models representing entities such as `User`, `Project`, `Room`, `Model`, `Recommendation`, `AnalysisResult`, `Task`, and more.
   - Handles relationships between entities (e.g., projects and rooms, models and materials).

3. **Schemas (`schemas/`)**:
   - Defines Pydantic schemas for data validation and serialization.
   - Used for input validation and response formatting in API endpoints.

4. **Routers (`routers/`)**:
   - Contains FastAPI routers for handling API requests.
   - Includes endpoints for authentication, project management, chat, recommendations, and more.

5. **Services (`services/`)**:
   - Provides business logic and utility functions.
   - Includes services for handling recommendations, validations, and other domain-specific logic.

6. **Main Application (`main.py`)**:
   - Entry point for the FastAPI application.
   - Registers routers, configures database connections, and starts the application.

7. **Dependencies (`requirements.txt`)**:
   - Lists all required Python packages for the project.

## Key Features

- **User Authentication**:
  - Supports user registration, login, and role-based access control.
  - Roles include `Client`, `Designer`, `Manager`, and `Consultant`.

- **Project Management**:
  - Allows users to create, view, and manage design projects.
  - Supports 3D modeling with integration of furniture, fixtures, and decorations.

- **Chat System**:
  - Enables communication between users, including private messages and project-specific discussions.
  - Supports consultation requests for design advice.

- **Recommendations and Analysis**:
  - Generates AI-powered recommendations for project improvements.
  - Analyzes project layouts, lighting, ergonomics, and cost efficiency.

- **Task Management**:
  - Allows creation and tracking of tasks related to projects, rooms, and models.
  - Supports task prioritization and status tracking.

## Object Model Implementation

The object model is implemented using SQLAlchemy ORM and defines the following key entities and relationships:

### Entities

1. **User**
   - Represents users with roles like `Client`, `Designer`, `Manager`, and `Consultant`.

2. **Project**
   - Represents a design project with attributes like `name`, `description`, and `status`.
   - Associated with a `User` (client) and optionally a `Designer`.

3. **Room**
   - Represents a room within a project, containing models and tasks.

4. **Model**
   - Represents a 3D model used in projects, with attributes like `name`, `type`, `dimensions`, and relationships to `Material`, `Room`, and `Task`.

5. **Material, Standard, and Catalog**
   - Represents materials used in models, standards for materials, and a catalog system for organizing materials.

6. **Recommendation**
   - Represents AI-powered recommendations for improving projects.

7. **Task**
   - Represents tasks related to projects, models, and rooms.

8. **Chat System**
   - Includes `ChatMessage`, `Consultation`, and `Comment` entities for communication and collaboration.

9. **Analysis Result**
   - Represents results of analysis for projects, such as layout, lighting, and cost efficiency.

### Example of Implementation

The `Model` entity is implemented as follows:

```python
from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from ..database import Base

class Model(Base):
    """
    Модель из диаграммы классов
    Attributes:
        - идМодели: int
        - каталог: string
        - размер: list<int>
        - тип: string
        - название: list<Мебель>
        - задание: list<Задание>
    Methods:
        - выбратьВариантРазмер(вариант: int): void
    """
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    catalog_id = Column(String)  # ID из каталога
    type = Column(String, nullable=False)  # furniture, fixture, decoration
    category = Column(String)  # kitchen, bathroom, living_room, bedroom

    # 3D данные модели
    file_url = Column(String)  # URL к .glb/.obj файлу
    thumbnail_url = Column(String)  # Превью модели

    # Размеры модели (в метрах)
    dimensions = Column(JSON)  # {width, height, depth}

    # Связь с помещением и проектом
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    room = relationship("Room", back_populates="models")

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    project = relationship("Project", back_populates="models")

    # Позиция в 3D пространстве
    position = Column(JSON)  # {x, y, z}
    rotation = Column(JSON)  # {x, y, z}
    scale = Column(JSON)  # {x, y, z}

    # Связь с материалами
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=True)
    material = relationship("Material", back_populates="models")

    # Relationships
    tasks = relationship("Task", back_populates="model")

    def __repr__(self):
        return f"<Model {self.name} ({self.type})>"
```

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure the Database**:
   - Update the database connection settings in [`database.py`](backend/database.py) to match your environment.

3. **Run the Application**:
   ```bash
   uvicorn main:app --reload
   ```

4. **Access the API**:
   - The API will be available at `http://127.0.0.1:8000`.
   - Use tools like Postman or the interactive API docs (`/docs`) to test endpoints.

## Development

- **Testing**:
  - Write unit tests for models, schemas, and services.
  - Use tools like `pytest` for testing.

- **Documentation**:
  - Keep the [`README.md`](backend/README.md) and API documentation up to date with changes to the project.
