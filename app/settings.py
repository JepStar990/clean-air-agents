"""
App settings and defaults.

Assumptions:
- Ollama is running locally at http://localhost:11434 (change OLLAMA_HOST if needed).
- Default locale is Johannesburg, ZA (switch via query params or here).
- OpenAQ v3 requires an API key (X-API-Key). Put OPENAQ_API_KEY in your environment or .env.
"""

from pydantic_settings import BaseSettings  # Pydantic v2: BaseSettings here


class Settings(BaseSettings):
    # Local LLM runtime (Ollama)
    OLLAMA_HOST: str = "http://localhost:11434"

    # Locale defaults
    DEFAULT_CITY: str = "Johannesburg"
    DEFAULT_COUNTRY: str = "ZA"  # ISO 3166-1 alpha-2

    # OpenAQ v3 API
    OPENAQ_API_BASE: str = "https://api.openaq.org/v3"
    OPENAQ_API_KEY: str | None = None  # set via env (X-API-Key header)

    # Feature flags
    PROMETHEUS_ENABLED: bool = True
    GLOBAL_DEFAULT: bool = False


settings = Settings()
