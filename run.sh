#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "Файл .env не найден. Создаю .env из шаблона .env.example..."
        cp .env.example .env
        echo "Пожалуйста, откройте .env и вставьте ваш BOT_TOKEN от @BotFather"
    fi
fi

python3 main.py
