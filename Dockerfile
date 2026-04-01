# Используем официальный образ Python 3.11 на базе дистрибутива Debian (версия slim для уменьшения размера)
FROM python:3.11-slim

# Запрещаем Python создавать файлы кэша .pyc (экономит место и ускоряет сборку)
ENV PYTHONDONTWRITEBYTECODE 1
# Отключаем буферизацию вывода (логи будут отображаться в реальном времени)
ENV PYTHONUNBUFFERED 1
# Указываем корневую директорию проекта в PYTHONPATH, чтобы импорты работали корректно
ENV PYTHONPATH /app

# Устанавливаем рабочую директорию внутри контейнера, где будут находиться все файлы проекта
WORKDIR /app

# Обновляем список пакетов и устанавливаем необходимые системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    # build-essential нужен для компиляции некоторых Python-пакетов
    build-essential \
    # libpq-dev необходим для работы с базой данных PostgreSQL (драйвер psycopg)
    libpq-dev \
    # git нужен, если какие-то зависимости устанавливаются напрямую из репозиториев
    git \
    # dos2unix используется для исправления окончаний строк (Windows CRLF -> Unix LF) в скриптах
    dos2unix \
    # Очищаем кэш apt-get для уменьшения финального размера Docker-образа
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем uv - сверхбыстрый менеджер пакетов для Python
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Копируем файл конфигурации зависимостей
COPY pyproject.toml /app/

# Копируем весь остальной код приложения в рабочую директорию контейнера
COPY . /app/

# Устанавливаем все зависимости и сам проект в системное окружение
RUN uv pip install --system -e .

# Копируем скрипт входа (entrypoint), который будет выполняться при запуске контейнера
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
# Конвертируем формат строк скрипта в Unix и даем права на его выполнение
RUN dos2unix /app/docker-entrypoint.sh && chmod +x /app/docker-entrypoint.sh

# Сообщаем Docker, что контейнер будет слушать порт 8000
EXPOSE 8000

# Команда по умолчанию, которая запускает наш скрипт инициализации при старте контейнера (используем bash)
CMD ["bash", "/app/docker-entrypoint.sh"]
