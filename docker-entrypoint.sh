#!/bin/bash

# Останавливаем выполнение скрипта при любой возникшей ошибке (флаг -e)
set -e

# --- Этап 1: Применение миграций базы данных PostgreSQL через Alembic ---
# Это гарантирует, что структура БД всегда актуальна при каждом запуске контейнера
echo "--- Applying PostgreSQL migrations ---"
alembic upgrade head

# --- Этап 2: Инициализация ClickHouse ---
# Создаем таблицу с моковыми данными (для аналитики), если её еще нет
echo "--- Initializing ClickHouse mock data ---"
uv run python scripts/init_clickhouse.py

# --- Этап 3: Запуск основного FastAPI приложения через Uvicorn ---
# --host 0.0.0.0 позволяет принимать запросы извне контейнера
# --port 8000 указывает порт для прослушивания
# --reload и --reload-dir src включают автоматическую перезагрузку сервера при изменении кода
echo "--- Starting FastAPI application ---"
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir src --reload-dir src
