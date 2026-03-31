# FastAPI Modular Architecture Rules

## Structure
The project follows a **Feature-based (Modular)** structure. Each domain/feature is encapsulated in `src/modules/<feature_name>/`.

### Module Structure (`src/modules/<feature>/`)
1. **`models.py`**: SQLAlchemy database models.
2. **`schemas.py`**: Pydantic models for validation and serialization.
3. **`repository.py`**: Data access logic (inherits from `BaseRepository`).
4. **`service.py`**: Business logic.
5. **`router.py`**: API routes for the module.

### Core Layers
- **`src/core/`**: Global configurations, security, base classes (e.g., `BaseRepository`).
- **`src/db/`**: Database connections (PostgreSQL session, ClickHouse client).
- **`src/api/v1/`**: Entry point for API versioning. Includes routers from modules.

## Conventions
- Use `AsyncSession` for SQLAlchemy database access.
- All business logic MUST reside in `service.py`.
- Repositories MUST only handle data persistence and retrieval.
- Dependency Injection should be used for database sessions and services.
- All routes should be versioned (e.g., `/api/v1/`).
- Use `pydantic-settings` for configuration management.
- **Comments and Docstrings must be in Russian.**
