# Bot_New

Основа для будущего Telegram-бота на стеке:

- Python
- aiogram 3
- PostgreSQL

Пока здесь нет логики бота. Созданы только базовые файлы проекта, настройки окружения и начальная структура базы данных.

## Где лежит проект

Windows:

```text
D:\Bot_New
```

WSL:

```text
/mnt/d/Bot_New
```

GitHub:

```text
https://github.com/Zhorik333/Bot_New
```

## Как ввести токен бота и id админ-группы

Не вставляй токен бота в чат. Лучше ввести его локально в терминале.

В WSL:

```bash
cd /mnt/d/Bot_New
bash scripts/set_local_env.sh
```

Скрипт попросит:

1. `BOT_TOKEN` — токен из BotFather.
2. `ADMIN_CHAT_ID` — id Telegram-группы админов.
3. `DATABASE_URL` — можно просто нажать Enter, чтобы оставить локальную базу:

```text
postgresql://bot_new:bot_new@127.0.0.1:5432/bot_new
```

Файл `.env` не добавляется в git.

## Локальная база PostgreSQL

Для разработки подготовлена база:

```text
database: bot_new
user: bot_new
password: bot_new
host: 127.0.0.1
port: 5432
```

Строка подключения:

```text
postgresql://bot_new:bot_new@127.0.0.1:5432/bot_new
```

## Структура

```text
bot/                 будущий код бота
docs/                документация и SQL-дизайн
migrations/          SQL-миграции базы
scripts/             локальные helper-скрипты
tests/               будущие тесты
.env.example         пример настроек без секретов
requirements.txt     будущие Python-зависимости
```


## Минимальный запуск бота

После заполнения `.env` бот можно запустить так:

```bash
cd /mnt/d/Bot_New
uv venv .venv
uv pip install -r requirements.txt
.venv/bin/python -m bot.main
```

Сейчас бот умеет только безопасно запускаться через polling и отвечать на `/start` простым тестовым сообщением. Основная логика заказов ещё не добавлена.

## Что делать дальше

Следующий безопасный шаг — сделать загрузчик конфигурации: читать `BOT_TOKEN`, `ADMIN_CHAT_ID` и `DATABASE_URL` из `.env`, но пока не запускать Telegram-бота.
