# Services Documentation

This document provides an overview of the services used in the backend, their purpose, and examples of how they are implemented. The services are designed to handle business logic, validations, and interactions with the database.

## Table of Contents

1. [CatalogService](#catalogservice)
2. [Corrector](#corrector)
3. [RecommendationSystem](#recommendation-system)
4. [Validator](#validator)

---

## CatalogService

### Purpose
The `CatalogService` is responsible for managing the catalog of materials, standards, and projects. It provides methods to filter materials, find standards, and retrieve detailed information about materials and their associated standards.

### Key Methods

1. **`get_plan_info(plan_id: int) -> Dict[str, Any]`**
   - Retrieves detailed information about a project (plan) by its ID.
   - Example usage:
     ```python
     catalog_service = CatalogService(db)
     plan_info = catalog_service.get_plan_info(plan_id=1)
     ```

2. **`filter_materials(criteria: Dict[str, Any]) -> List[Material]`**
   - Filters materials based on specific criteria such as type, name, or properties.
   - Example usage:
     ```python
     materials = catalog_service.filter_materials(criteria={"type": "wood", "name": "oak"})
     ```

3. **`find_standard(plan_id: int, criteria: Optional[Dict[str, Any]] = None) -> List[Standard]`**
   - Finds standards for a project based on optional criteria.
   - Example usage:
     ```python
     standards = catalog_service.find_standard(plan_id=1, criteria={"category": "fire_safety"})
     ```

4. **`get_material_with_standards(material_id: int) -> Dict[str, Any]`**
   - Retrieves a material along with its associated standards.
   - Example usage:
     ```python
     material_info = catalog_service.get_material_with_standards(material_id=1)
     ```

### Example Code

```python
from sqlalchemy.orm import Session
from backend.services.catalog_service import CatalogService

# Initialize the service with a database session
db: Session = ...  # Your database session
catalog_service = CatalogService(db)

# Get project info
plan_info = catalog_service.get_plan_info(plan_id=1)
print(plan_info)

# Filter materials
materials = catalog_service.filter_materials(criteria={"type": "wood", "name": "oak"})
print(materials)

# Find standards for a project
standards = catalog_service.find_standard(plan_id=1, criteria={"category": "fire_safety"})
print(standards)

# Get material with standards
material_info = catalog_service.get_material_with_standards(material_id=1)
print(material_info)
```

---

## Corrector

### Purpose
The `Corrector` service is responsible for optimizing the placement and orientation of models within a room or project. It ensures that models are positioned correctly and adhere to ergonomic and design principles.

### Key Methods

1. **`optimize_model(model: Model) -> CorrectionResult`**
   - Optimizes the position and orientation of a single model within a room.
   - Example usage:
     ```python
     corrector = Corrector(db)
     result = corrector.optimize_model(model)
     ```

2. **`optimize_room_layout(room_id: int) -> CorrectionResult`**
   - Optimizes the layout of all models within a room.
   - Example usage:
     ```python
     result = corrector.optimize_room_layout(room_id=1)
     ```

3. **`optimize_project(project_id: int) -> CorrectionResult`**
   - Optimizes the layout of all rooms and models within a project.
   - Example usage:
     ```python
     result = corrector.optimize_project(project_id=1)
     ```

### Example Code

```python
from sqlalchemy.orm import Session
from backend.services.corrector import Corrector
from backend.models.model import Model

# Initialize the service with a database session
db: Session = ...  # Your database session
corrector = Corrector(db)

# Optimize a single model
model = db.query(Model).filter(Model.id == 1).first()
result = corrector.optimize_model(model)
print(result.to_dict())

# Optimize a room layout
result = corrector.optimize_room_layout(room_id=1)
print(result.to_dict())

# Optimize an entire project
result = corrector.optimize_project(project_id=1)
print(result.to_dict())
```

---

## Recommendation System

### Purpose
The `RecommendationSystem` is designed to generate AI-powered recommendations for improving projects. It includes methods for creating recommendations, suggesting alternatives, and analyzing project layouts.

### Key Methods

1. **`create_recommendation(recommendation_id: int, data: Dict[str, Any]) -> Recommendation`**
   - Creates a recommendation based on provided data.
   - Example usage:
     ```python
     system = RecommendationSystem(db)
     recommendation = system.create_recommendation(
         recommendation_id=1,
         data={"project_id": 1, "type": "layout"}
     )
     ```

2. **`suggest_alternatives(project: Project) -> List[Recommendation]`**
   - Suggests alternative solutions for a project.
   - Example usage:
     ```python
     alternatives = system.suggest_alternatives(project)
     ```

3. **`analyze_project_layout(project_id: int) -> Dict[str, Any]`**
   - Analyzes the layout of a project and provides recommendations.
   - Example usage:
     ```python
     analysis = system.analyze_project_layout(project_id=1)
     ```

### Example Code

```python
from sqlalchemy.orm import Session
from backend.services.recommendation_system import RecommendationSystem
from backend.models.project import Project

# Initialize the service with a database session
db: Session = ...  # Your database session
system = RecommendationSystem(db)

# Create a recommendation
recommendation = system.create_recommendation(
    recommendation_id=1,
    data={"project_id": 1, "type": "layout"}
)
print(recommendation)

# Suggest alternatives for a project
project = db.query(Project).filter(Project.id == 1).first()
alternatives = system.suggest_alternatives(project)
print(alternatives)

# Analyze a project layout
analysis = system.analyze_project_layout(project_id=1)
print(analysis)
```

---

## Validator

### Purpose
The `Validator` service ensures that models, rooms, and projects comply with standards and regulations. It performs checks for dimensions, positions, and material standards.

### Key Methods

1. **`validate_model(model: Model) -> ValidationResult`**
   - Validates a model to ensure it meets the required standards.
   - Example usage:
     ```python
     validator = Validator(db)
     result = validator.validate_model(model)
     ```

2. **`validate_room(room: Room) -> ValidationResult`**
   - Validates a room to ensure it complies with regulations.
   - Example usage:
     ```python
     result = validator.validate_room(room)
     ```

3. **`validate_project(project_id: int) -> ValidationResult`**
   - Validates an entire project to ensure all rooms and models are compliant.
   - Example usage:
     ```python
     result = validator.validate_project(project_id=1)
     ```

### Example Code

```python
from sqlalchemy.orm import Session
from backend.services.validator import Validator
from backend.models.model import Model
from backend.models.room import Room

# Initialize the service with a database session
db: Session = ...  # Your database session
validator = Validator(db)

# Validate a model
model = db.query(Model).filter(Model.id == 1).first()
result = validator.validate_model(model)
print(result.to_dict())

# Validate a room
room = db.query(Room).filter(Room.id == 1).first()
result = validator.validate_room(room)
print(result.to_dict())

# Validate an entire project
result = validator.validate_project(project_id=1)
print(result.to_dict())
```

---

This document provides a comprehensive overview of the services used in the backend, their functionality, and examples of how to implement and use them in code.