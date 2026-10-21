import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


class Settings:
    app_env = os.getenv("APP_ENV", "development").lower()
    app_internal_token = os.getenv("APP_INTERNAL_TOKEN", "")
    database_url = os.getenv("DATABASE_URL", f"sqlite:///{(ROOT / 'venufin.db').as_posix()}")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    brave_search_api_key = os.getenv("BRAVE_SEARCH_API_KEY", "")
    alphavantage_api_key = os.getenv("ALPHAVANTAGE_API_KEY", "")
    market_data_entitlement = os.getenv("MARKET_DATA_ENTITLEMENT", "")
    embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    embeddings_enabled = os.getenv("EMBEDDINGS_ENABLED", "true").lower() == "true"
    sec_user_agent = os.getenv("SEC_USER_AGENT", "VenuFinAI contact@example.com")
    rss_urls = [u.strip() for u in os.getenv("NEWS_RSS_URLS", "").split(",") if u.strip()]
    cors_origins = [u.strip().rstrip("/") for u in os.getenv("CORS_ORIGINS", "http://127.0.0.1:3000,http://localhost:3000").split(",") if u.strip()]
    max_upload_mb = int(os.getenv("MAX_UPLOAD_MB", "25"))
    rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))


settings = Settings()
STORAGE = Path(os.getenv("UPLOADS_DIR") or str(ROOT / "storage" / "uploads")).expanduser()
STORAGE.mkdir(parents=True, exist_ok=True)
