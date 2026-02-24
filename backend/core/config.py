"""
Centralized configuration loaded from environment variables.
Uses pydantic-settings for validation and type coercion.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── LLM API Keys ──────────────────────────────────────────
    cerebras_api_key: str = ""
    openai_api_key: str = ""
    siliconflow_api_key: str = ""

    # ── LLM Endpoints ─────────────────────────────────────────
    cerebras_base_url: str = "https://api.cerebras.ai/v1"
    cerebras_model: str = "gpt-oss-120b"
    openai_model: str = "gpt-4.1-nano"
    siliconflow_base_url: str = "https://api.siliconflow.cn/v1"
    siliconflow_model: str = "Qwen/Qwen2.5-Coder-7B-Instruct"

    # ── Database ───────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://cofounder:cofounder@localhost:5432/cofounder"

    # ── GitHub OAuth ───────────────────────────────────────────
    github_client_id: str = ""
    github_client_secret: str = ""

    # ── App ────────────────────────────────────────────────────
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    nextauth_secret: str = ""
    nextauth_url: str = "http://localhost:3000"

    # ── Rate Limiting ──────────────────────────────────────────
    siliconflow_rpm_limit: int = 1000
    siliconflow_backoff_base: float = 1.0
    siliconflow_backoff_max: float = 60.0


settings = Settings()
