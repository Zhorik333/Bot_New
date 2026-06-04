import asyncio
import tempfile
import unittest
from pathlib import Path

from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode

from bot.config import Config
from bot.main import create_bot, create_dispatcher, main, run_polling


class RuntimeTests(unittest.TestCase):
    def test_create_bot_uses_token_and_html_parse_mode(self):
        config = Config(
            bot_token="123456:ABCDEF_FAKE_TOKEN_REPLACE_ME",
            admin_chat_id=-1001234567890,
            database_url="postgresql://bot_new:bot_new@127.0.0.1:5432/bot_new",
        )

        bot = create_bot(config)

        self.assertIsInstance(bot, Bot)
        self.assertEqual(bot.token, config.bot_token)
        self.assertEqual(bot.default.parse_mode, ParseMode.HTML)

    def test_create_dispatcher_includes_supplied_router(self):
        router = Router(name="test-router")

        dispatcher = create_dispatcher(router)

        self.assertIsInstance(dispatcher, Dispatcher)
        self.assertIn(router, dispatcher.sub_routers)

    def test_create_dispatcher_without_arguments_includes_client_router(self):
        dispatcher = create_dispatcher()

        router_names = {router.name for router in dispatcher.sub_routers}
        self.assertIn("client", router_names)

    def test_run_polling_deletes_webhook_before_starting_polling(self):
        calls = []

        class FakeBot:
            async def delete_webhook(self, *, drop_pending_updates):
                calls.append(("delete_webhook", drop_pending_updates))

        class FakeDispatcher:
            async def start_polling(self, bot):
                calls.append(("start_polling", bot))

        fake_bot = FakeBot()
        asyncio.run(run_polling(fake_bot, FakeDispatcher()))

        self.assertEqual(calls[0], ("delete_webhook", True))
        self.assertEqual(calls[1], ("start_polling", fake_bot))

    def test_main_loads_config_and_uses_injected_polling_function(self):
        env_path = self.write_env(
            "BOT_TOKEN=123456:ABCDEF_FAKE_TOKEN_REPLACE_ME\n"
            "ADMIN_CHAT_ID=-1001234567890\n"
            "DATABASE_URL=postgresql://bot_new:bot_new@127.0.0.1:5432/bot_new\n"
        )
        seen = {}

        async def fake_run_polling(bot, dispatcher):
            seen["bot_token"] = bot.token
            seen["router_count"] = len(dispatcher.sub_routers)

        main(env_path=env_path, run_polling_func=fake_run_polling)

        self.assertEqual(seen["bot_token"], "123456:ABCDEF_FAKE_TOKEN_REPLACE_ME")
        self.assertGreaterEqual(seen["router_count"], 1)

    def write_env(self, content: str) -> Path:
        tmp = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False)
        self.addCleanup(lambda: Path(tmp.name).unlink(missing_ok=True))
        tmp.write(content)
        tmp.close()
        return Path(tmp.name)


if __name__ == "__main__":
    unittest.main()
