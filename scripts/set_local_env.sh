#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

DEFAULT_DATABASE_URL="postgresql://bot_new:bot_new@127.0.0.1:5432/bot_new"

printf "Enter BOT_TOKEN from BotFather. It will not be shown: "
stty -echo
read -r BOT_TOKEN
stty echo
printf "\n"

printf "Enter ADMIN_CHAT_ID, for example -1001234567890: "
read -r ADMIN_CHAT_ID

printf "Enter DATABASE_URL or press Enter for local default [%s]: " "$DEFAULT_DATABASE_URL"
read -r DATABASE_URL
DATABASE_URL="${DATABASE_URL:-$DEFAULT_DATABASE_URL}"

if [ -z "$BOT_TOKEN" ]; then
  echo "BOT_TOKEN is empty. .env was not changed." >&2
  exit 1
fi

if [ -z "$ADMIN_CHAT_ID" ]; then
  echo "ADMIN_CHAT_ID is empty. .env was not changed." >&2
  exit 1
fi

umask 077
cat > .env <<EOF
BOT_TOKEN=$BOT_TOKEN
ADMIN_CHAT_ID=$ADMIN_CHAT_ID
DATABASE_URL=$DATABASE_URL
DEFAULT_LANGUAGE=ru
DEFAULT_TZ=Europe/Belgrade
LOG_LEVEL=INFO
EOF

echo ".env created locally. It is ignored by git."
