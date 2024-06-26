import secrets
from typing import Annotated, Any, Literal
from pydantic import (AnyUrl,BeforeValidator,computed_field)
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    DOMAIN: str = "localhost"
    ENVIRONMENT: Literal["local", "tests", "staging", "production"] = "local"

    @property
    def DATABASE_URL(self) -> str:
        match self.ENVIRONMENT:
            case "local":
                return "sqlite:///database.db"
            case "tests":
                return "sqlite:///database.db"#self._database_url
            case "staging":
                return "postgresql://postgres:postgres@localhost:5432/postgres"
            case "production":
                return "postgresql://postgres:postgres@localhost:5432/postgres"
            case _:
                raise ValueError(f"Invalid environment: {self.ENVIRONMENT}")


    @computed_field  # type: ignore[misc]
    @property
    def server_host(self) -> str:
        # Use HTTPS for anything other than local development
        if self.ENVIRONMENT == "local":
            return f"http://{self.DOMAIN}"
        return f"https://{self.DOMAIN}"

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        []
    )


settings = Settings()  # type: ignore
