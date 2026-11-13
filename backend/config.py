"""
backend/config.py
-----------------
Reads configuration from .env and exposes SQLAlchemy engine + session factory.
Supports dual-database engines:
- SQLite (default for local, zero-setup evaluation, and automated testing)
- PostgreSQL (for staging, production, and high-concurrency deployments)
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

# Load .env from repo root (two levels up from backend/)
REPO_ROOT = Path(__file__).resolve().parent.parent
_ENV_PATH = REPO_ROOT / ".env"
load_dotenv(_ENV_PATH)

# Default to SQLite at data/campus.db if DATABASE_URL is not set or empty
_DEFAULT_SQLITE_PATH = REPO_ROOT / "data" / "campus.db"
DATABASE_URL: str = os.environ.get("DATABASE_URL", "").strip()
if not DATABASE_URL:
    DATABASE_URL = f"sqlite:///{_DEFAULT_SQLITE_PATH}"

try:
    _database_url = make_url(DATABASE_URL)
except Exception as exc:
    raise RuntimeError("DATABASE_URL must be a valid SQLAlchemy database URL.") from exc

_backend_name = _database_url.get_backend_name()
if _backend_name not in ("postgresql", "postgres", "sqlite"):
    raise RuntimeError("DATABASE_URL must target PostgreSQL or SQLite.")

ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development").strip().lower()

_SECRET_PLACEHOLDERS = {
    "",
    "your-32-byte-random-secret-key-here",
    "super-secret-key-for-dev-change-to-a-long-random-secret-at-least-32-bytes",
    "change-me",
    "changeme",
    "your-secret-key",
}
SECRET_KEY: str = os.environ.get("SECRET_KEY", "").strip()
if SECRET_KEY.lower() in _SECRET_PLACEHOLDERS or len(SECRET_KEY.encode("utf-8")) < 32:
    if ENVIRONMENT == "production":
        raise ValueError(
            "SECRET_KEY must be configured with a non-placeholder value of at least 32 bytes in production."
        )
    # Safe deterministic fallback for development and testing
    SECRET_KEY = "rio-mjp-development-secret-key-32-bytes-minimum-security-token"

ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 20
REFRESH_TOKEN_EXPIRE_DAYS: int = 7
# Secure cookies are mandatory in production; local HTTP development may opt out.
COOKIE_SECURE: bool = ENVIRONMENT == "production" or os.environ.get("COOKIE_SECURE", "false").strip().lower() in {"1", "true", "yes"}

# SQLAlchemy 2.0 engine configuration
if _backend_name == "sqlite":
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    # pool_pre_ping=True keeps the connection alive on Windows where idle
    # connections can be dropped by the OS or the Postgres server.
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Multi-Provider LLM Configuration (Groq, Gemini, Ollama, Anthropic)
GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "").strip()
GROQ_MODEL: str = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_MODEL: str = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash").strip()

OLLAMA_BASE_URL: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").strip()
OLLAMA_MODEL: str = os.environ.get("OLLAMA_MODEL", "llama3").strip()

ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "").strip()
ANTHROPIC_MODEL: str = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022").strip()
