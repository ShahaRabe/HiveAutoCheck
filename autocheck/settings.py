from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    segel_gitlab_host: str
    segel_gitlab_token: str

    hanich_gitlab_host: str
    hanich_gitlab_token: str

    tests_repository_url: str
    tests_repository_ref: str

    logging_level: str = "WARNING"

    hive_input_json_path: Path = Path("/mnt/autocheck/input.json'")


settings = Settings()
