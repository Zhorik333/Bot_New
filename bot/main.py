from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from pathlib import Path

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.config import Config, load_config


async def handle_start(message: Message) -> None:
    await message.answer("Бот запущен. Основа проекта работает.")


def create_client_router() -> Router:
    router = Router(name="client")
    router.message.register(handle_start, CommandStart())
    return router


def create_bot(config: Config) -> Bot:
    return Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher(*routers: Router) -> Dispatcher:
    dispatcher = Dispatcher()
    routers_to_include = routers or (create_client_router(),)
    dispatcher.include_routers(*routers_to_include)
    return dispatcher


async def run_polling(bot: Bot, dispatcher: Dispatcher) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


def main(
    env_path: str | Path = ".env",
    run_polling_func: Callable[[Bot, Dispatcher], Awaitable[None]] = run_polling,
) -> None:
    config = load_config(env_path)
    bot = create_bot(config)
    dispatcher = create_dispatcher()
    asyncio.run(run_polling_func(bot, dispatcher))


if __name__ == "__main__":
    main()
