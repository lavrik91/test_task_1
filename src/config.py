from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel


# Logging Settings
class LoggingSettings(BaseModel):
    """Configure the logging engine."""

    # The time field can be formatted using more human-friendly tokens.
    # These constitute a subset of the one used by the Pendulum library
    # https://pendulum.eustace.io/docs/#tokens
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level: <5} | {message}"

    # The .log filename
    file: str = "backend"

    # The .log filename for Celery
    file_celery: str = "worker"

    # The .log file Rotation
    rotation: str = "1MB"

    # The type of compression
    compression: str = "zip"


class Settings(BaseSettings):
    MODE: str

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    RMQ_LOGIN: str
    RMQ_PASSWORD: str
    RMQ_HOST: str
    RMQ_PORT: int

    REDIS_URL: str

    ROOT_PATH: Path = Path(__file__).parent.parent

    LOGGING: LoggingSettings = LoggingSettings()

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def RABBIT_URL(self):
        return f"amqp://{self.RMQ_LOGIN}:{self.RMQ_PASSWORD}@{self.RMQ_HOST}:{self.RMQ_PORT}/"

    model_config = SettingsConfigDict(env_file=str(Path(__file__).parent.parent / ".env.dev"))


settings = Settings()
