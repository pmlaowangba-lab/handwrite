from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="HW_BACKEND_", extra="ignore")

    app_name: str = "Handwrite Backend"
    app_env: str = "dev"
    app_debug: bool = True
    app_version: str = "0.1.0"

    host: str = "0.0.0.0"
    port: int = 9000

    backend_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[2])
    project_root: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[3])

    database_url: str | None = None
    render_scale: float = 0.5
    ai_base_url: str = "https://api.openai.com"
    ai_api_key: str | None = None
    ai_model: str = "gpt-5.3-codex"
    ai_timeout_seconds: int = 90
    ai_max_tokens: int = 4096

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        db_file = self.backend_dir / "app.db"
        return f"sqlite:///{db_file}"

    @property
    def assets_dir(self) -> Path:
        return self.project_root / "assets"

    @property
    def fonts_dir(self) -> Path:
        return self.assets_dir / "fonts"

    @property
    def papers_dir(self) -> Path:
        return self.assets_dir / "papers" / "processed"

    @property
    def storage_dir(self) -> Path:
        return self.backend_dir / "storage"

    @property
    def render_dir(self) -> Path:
        return self.storage_dir / "renders"


@lru_cache
def get_settings() -> Settings:
    return Settings()
