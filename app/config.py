import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env", override=True)


def _build_url(prefix: str | None = None) -> str | None:
    # allow DB_WRITER_URL / DB_READER_URL full strings first
    if prefix:
        full = os.getenv(f"DB_{prefix}_URL")
        if full:
            return full
    else:
        full = os.getenv("DATABASE_URL")
        if full:
            return full

    # fall back to parts (PG_* or PG_<PREFIX>_*)
    def env(k: str, default: str | None = None) -> str | None:
        return os.getenv(k, default)

    def pick(k: str, default: str | None = None) -> str | None:
        return env(f"PG_{prefix}_{k}") if prefix else env(f"PG_{k}") or default

    host = pick("HOST") or env("PG_HOST")
    port = pick("PORT", "5432")
    db   = pick("DB", env("PG_DB", "appdb"))
    user = pick("USER", env("PG_USER", "postgres"))
    pwd  = pick("PASSWORD", env("PG_PASSWORD", "postgres"))
    if not host:
        return None
    return f"postgresql+asyncpg://{user}:{quote_plus(pwd)}@{host}:{port}/{db}"


class Settings:
    # legacy single URL (treated as writer)
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")
    DB_WRITER_URL: str | None = os.getenv("DB_WRITER_URL") or _build_url("WRITER")
    DB_READER_URL: str | None = os.getenv("DB_READER_URL") or _build_url("READER")

    def writer_url(self) -> str:
        return self.DB_WRITER_URL or self.DATABASE_URL or _build_url("WRITER") or _build_url()

    def reader_url(self) -> str:
        # fallback to writer to avoid crashes during migration
        return self.DB_READER_URL or self.writer_url()


settings = Settings()