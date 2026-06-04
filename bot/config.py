from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import dotenv_values
except ModuleNotFoundError:  # pragma: no cover - fallback for bare stdlib test runs
    dotenv_values = None


class ConfigError(ValueError):
    """Raised when required application configuration is missing or invalid."""


@dataclass(frozen=True)
class Config:
    bot_token: str = field(repr=False)
    admin_chat_id: int
    database_url: str
    default_language: str = "ru"
    default_tz: str = "Europe/Belgrade"
    review_delay_minutes: int = 30
    log_level: str = "INFO"

    def __repr__(self) -> str:
        return (
            "Config("
            "bot_token=<hidden>, "
            f"admin_chat_id={self.admin_chat_id!r}, "
            f"database_url={self.database_url!r}, "
            f"default_language={self.default_language!r}, "
            f"default_tz={self.default_tz!r}, "
            f"review_delay_minutes={self.review_delay_minutes!r}, "
            f"log_level={self.log_level!r}"
            ")"
        )


def load_config(env_path: str | Path = ".env") -> Config:
    values = _load_env_values(Path(env_path))

    return Config(
        bot_token=_required_str(values, "BOT_TOKEN"),
        admin_chat_id=_required_int(values, "ADMIN_CHAT_ID"),
        database_url=_required_str(values, "DATABASE_URL"),
        default_language=_optional_str(values, "DEFAULT_LANGUAGE", "ru"),
        default_tz=_optional_str(values, "DEFAULT_TZ", "Europe/Belgrade"),
        review_delay_minutes=_optional_int(values, "REVIEW_DELAY_MINUTES", 30),
        log_level=_optional_str(values, "LOG_LEVEL", "INFO"),
    )


def _load_env_values(env_path: Path) -> dict[str, str]:
    file_values: dict[str, str] = {}
    if env_path.exists():
        if dotenv_values is not None:
            file_values = {
                key: value
                for key, value in dotenv_values(env_path).items()
                if key and value is not None
            }
        else:
            file_values = _parse_env_file(env_path)

    merged = dict(file_values)
    for key in {
        "BOT_TOKEN",
        "ADMIN_CHAT_ID",
        "DATABASE_URL",
        "DEFAULT_LANGUAGE",
        "DEFAULT_TZ",
        "REVIEW_DELAY_MINUTES",
        "LOG_LEVEL",
    }:
        if key in os.environ:
            merged[key] = os.environ[key]
    return merged


def _parse_env_file(env_path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _required_str(values: dict[str, str], key: str) -> str:
    value = values.get(key, "").strip()
    if not value:
        raise ConfigError(f"Missing required config value: {key}")
    return value


def _optional_str(values: dict[str, str], key: str, default: str) -> str:
    return values.get(key, default).strip() or default


def _required_int(values: dict[str, str], key: str) -> int:
    value = _required_str(values, key)
    try:
        return int(value)
    except ValueError as exc:
        raise ConfigError(f"Invalid integer config value: {key}") from exc


def _optional_int(values: dict[str, str], key: str, default: int) -> int:
    value = values.get(key)
    if value is None or not value.strip():
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ConfigError(f"Invalid integer config value: {key}") from exc
