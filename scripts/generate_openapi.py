import json

from src.main import app


def generate_openapi():
    """Генерация и сохранение OpenAPI схемы в файл openapi.json."""
    openapi_schema = app.openapi()
    with open("openapi.json", "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
    print("OpenAPI схема успешно сгенерирована в openapi.json")


if __name__ == "__main__":
    generate_openapi()
