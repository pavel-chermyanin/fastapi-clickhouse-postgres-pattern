# Coding Standards

## Python Style
1. Use `black` for formatting.
2. Use `isort` for imports sorting.
3. Type hinting is mandatory for all function parameters and return values.
4. Docstrings (Google format) are required for complex services and business logic.
5. Use `async/await` for all I/O bound operations (database, external APIs).

## Naming Conventions
- Variables/Functions: `snake_case`.
- Classes: `PascalCase`.
- Modules: `snake_case`.
- Constants: `SCREAMING_SNAKE_CASE`.

## Error Handling
- Use custom exception classes defined in `src/core/exceptions.py`.
- Handle expected errors gracefully and return appropriate HTTP status codes.
- Do not expose internal database errors to the API clients.
