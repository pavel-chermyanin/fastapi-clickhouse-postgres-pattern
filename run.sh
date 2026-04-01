#!/bin/bash

# Скрипт-обертка для запуска приложения на Linux/macOS

if command -v python3 &>/dev/null; then
    python3 run.py "$@"
else
    python run.py "$@"
fi
