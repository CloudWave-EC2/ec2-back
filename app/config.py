# app/config.py
import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env", override=True)


def _build_url(prefix: str | None = None) -> str | None:
    # full URL first
    if prefix:
        full = os.getenv(f"{prefix}_URL") or os.getenv(f"DB_{prefix}_URL")
        if full:
            return full
    full = os.getenv("DATABASE_URL")
    if full:
        return full

    # parts fallback (PG_* or PG_<PREFIX>_*)
    def pick(key: str, default: str | None = None) -> str | None:
        if prefix:
            return os.getenv(f"PG_{prefix}_{key}") or os.getenv(f"PG_{key}") or default
        return os.getenv(f"PG_{key}") or default

    host = pick("HOST", "127.0.0.1")
    port = pick("PORT", "5432")
    db   = pick("DB", "testdb")
    user = pick("USER", "testuser")
    pwd  = pick("PASSWORD", "dbpassword")
    return f"postgresql+asyncpg://{user}:{quote_plus(pwd)}@{host}:{port}/{db}"


class Settings:
    # legacy single URL
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")
    DB_WRITER_URL: str | None = os.getenv("DB_WRITER_URL") or _build_url("WRITER")
    DB_READER_URL: str | None = os.getenv("DB_READER_URL") or _build_url("READER")

    def writer_url(self) -> str:
        return self.DB_WRITER_URL or self.DATABASE_URL or _build_url("WRITER")

    def reader_url(self) -> str:
        return self.DB_READER_URL or self.writer_url()


settings = Settings()