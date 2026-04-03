#!/bin/bash

# Останавливаем выполнение скрипта при любой возникшей ошибке (флаг -e)
set -e

# --- Этап 1: Применение миграций базы данных PostgreSQL через Alembic ---
# Это гарантирует, что структура БД всегда актуальна при каждом запуске контейнера
echo "--- Applying PostgreSQL migrations ---"
alembic upgrade head

# --- Этап 2: Генерация и запуск сервера визуализации БД ---
echo "--- Generating DB schema and starting visualization server ---"
# Генерируем схему из текущих моделей
python scripts/generate_schema.py
# Запускаем сервер визуализации в фоновом режиме (порт 8080)
python scripts/serve_schema.py &

# --- Этап 4: Запуск основного FastAPI приложения через Uvicorn ---
# --host 0.0.0.0 позволяет принимать запросы извне контейнера
# --port 8000 указывает порт для прослушивания
# --reload и --reload-dir src включают автоматическую перезагрузку сервера при изменении кода
echo "--- Starting FastAPI application ---"
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir src
