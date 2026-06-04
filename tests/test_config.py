import os
import tempfile
import unittest
from pathlib import Path

from bot.config import ConfigError, load_config


class LoadConfigTests(unittest.TestCase):
    def write_env(self, content: str) -> Path:
        tmp = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False)
        self.addCleanup(lambda: Path(tmp.name).unlink(missing_ok=True))
        tmp.write(content)
        tmp.close()
        return Path(tmp.name)

    def test_loads_required_values_and_defaults(self):
        env_path = self.write_env(
            "BOT_TOKEN=123456:ABCDEF_FAKE_TOKEN_REPLACE_ME\n"
            "ADMIN_CHAT_ID=-1001234567890\n"
            "DATABASE_URL=postgresql://bot_new:bot_new@127.0.0.1:5432/bot_new\n"
        )

        config = load_config(env_path)

        self.assertEqual(config.bot_token, "123456:ABCDEF_FAKE_TOKEN_REPLACE_ME")
        self.assertEqual(config.admin_chat_id, -1001234567890)
        self.assertEqual(config.database_url, "postgresql://bot_new:bot_new@127.0.0.1:5432/bot_new")
        self.assertEqual(config.default_language, "ru")
        self.assertEqual(config.default_tz, "Europe/Belgrade")
        self.assertEqual(config.review_delay_minutes, 30)
        self.assertEqual(config.log_level, "INFO")

    def test_environment_variables_override_env_file(self):
        env_path = self.write_env(
            "BOT_TOKEN=123456:FROM_FILE_TOKEN_REPLACE_ME\n"
            "ADMIN_CHAT_ID=-1001111111111\n"
            "DATABASE_URL=postgresql://file:file@127.0.0.1:5432/file\n"
        )
        old = os.environ.get("ADMIN_CHAT_ID")
        os.environ["ADMIN_CHAT_ID"] = "-1002222222222"
        self.addCleanup(self.restore_env, "ADMIN_CHAT_ID", old)

        config = load_config(env_path)

        self.assertEqual(config.admin_chat_id, -1002222222222)

    def test_missing_required_key_raises_clear_error(self):
        env_path = self.write_env(
            "BOT_TOKEN=123456:ABCDEF_FAKE_TOKEN_REPLACE_ME\n"
            "DATABASE_URL=postgresql://bot_new:bot_new@127.0.0.1:5432/bot_new\n"
        )

        with self.assertRaisesRegex(ConfigError, "ADMIN_CHAT_ID"):
            load_config(env_path)

    def test_invalid_integer_raises_clear_error(self):
        env_path = self.write_env(
            "BOT_TOKEN=123456:ABCDEF_FAKE_TOKEN_REPLACE_ME\n"
            "ADMIN_CHAT_ID=not-a-number\n"
            "DATABASE_URL=postgresql://bot_new:bot_new@127.0.0.1:5432/bot_new\n"
        )

        with self.assertRaisesRegex(ConfigError, "ADMIN_CHAT_ID"):
            load_config(env_path)

    def test_repr_does_not_expose_bot_token(self):
        env_path = self.write_env(
            "BOT_TOKEN=123456:SECRET_TOKEN_SHOULD_NOT_BE_IN_REPR\n"
            "ADMIN_CHAT_ID=-1001234567890\n"
            "DATABASE_URL=postgresql://bot_new:bot_new@127.0.0.1:5432/bot_new\n"
        )

        config = load_config(env_path)

        self.assertNotIn("SECRET_TOKEN_SHOULD_NOT_BE_IN_REPR", repr(config))
        self.assertIn("bot_token", repr(config))

    @staticmethod
    def restore_env(key: str, old_value: str | None) -> None:
        if old_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = old_value


if __name__ == "__main__":
    unittest.main()
