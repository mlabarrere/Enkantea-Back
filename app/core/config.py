import secrets
from typing import Annotated, Any, Literal
from pydantic import AnyUrl, BeforeValidator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from passlib.context import CryptContext


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
    PROJECT_NAME: str = "Enkantea"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)

    # Hashing
    pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Tokens
    TOKEN_ALGORITHM: str = "HS512"
    TOKEN_SECRET: str = (
        "harkaitza"  # "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7" # random
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = (
        50  # 60 * 24 * 8 # 60 minutes * 24 hours * 8 days = 8 days
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REFRESH_TOKEN_SECRET: str = (
        "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    )

    DOMAIN: str = "localhost"
    ENVIRONMENT: Literal["local", "tests", "staging", "production"] = "local"

    @property
    def DATABASE_URL(self) -> str:
        match self.ENVIRONMENT:
            case "local":
                return "sqlite:///database.db"
            case "tests":
                return "sqlite:///database.db"  # self._database_url
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
