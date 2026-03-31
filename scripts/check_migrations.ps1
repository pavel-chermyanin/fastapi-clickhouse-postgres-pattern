# Скрипт для проверки наличия незафиксированных изменений в моделях
# Используется в pre-commit хуке для предотвращения пуша без миграций

Write-Host "Проверка миграций базы данных..." -ForegroundColor Cyan

# Определяем путь к alembic в виртуальном окружении
$alembic_path = "venv\Scripts\alembic.exe"
if (!(Test-Path $alembic_path)) {
    # Для Linux/macOS если запускается из-под git bash
    $alembic_path = "venv/bin/alembic"
}

if (!(Test-Path $alembic_path)) {
    Write-Host "Alembic не найден в venv. Пропуск проверки." -ForegroundColor Yellow
    exit 0
}

# Попытка проверить наличие изменений
try {
    # Запускаем alembic через python в venv для надежности
    $python_path = "venv\Scripts\python.exe"
    if (!(Test-Path $python_path)) { $python_path = "venv/bin/python" }

    & $python_path -m alembic check
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ОШИБКА: Обнаружены изменения в моделях, для которых не созданы миграции!" -ForegroundColor Red
        Write-Host "Пожалуйста, выполните: .\venv\Scripts\python.exe -m alembic revision --autogenerate -m 'ваше сообщение'" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "Миграции в порядке." -ForegroundColor Green
} catch {
    Write-Host "Ошибка при выполнении alembic check. Убедитесь, что база данных доступна." -ForegroundColor Yellow
    exit 0
}
