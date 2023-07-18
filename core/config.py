from pydantic import BaseSettings


class Settings(BaseSettings):
    DOCKER_PATH = "/core"
    SECRET = "SECRET"
    ALLOW_HOST = "http://localhost:3000"
    RP_ID = "localhost"
    RP_NAME = "App"
    EXPECTED_ORIGIN = "http://localhost:3000"
    TIMEOUT = "60000"
    FILE_PATH = "data/files"

    class Config:
        env_file = ".env"


settings = Settings()
