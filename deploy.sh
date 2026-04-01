#!/bin/bash

# Скрипт-обертка для запуска развертывания на Linux/macOS
# Автоматически определяет правильную команду python

if command -v python3 &>/dev/null; then
    python3 scripts/deploy.py "$@"
else
    python scripts/deploy.py "$@"
fi
