#!/bin/bash

# Выход при любой ошибке
set -e

# 1. Применяем миграции Alembic
echo "--- Applying database migrations ---"
alembic upgrade head

# 2. Запускаем основное приложение
echo "--- Starting FastAPI application ---"
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir src --reload-dir src
