from pathlib import Path
from pydantic import HttpUrl

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    segel_gitlab_host: str
    segel_gitlab_token: str

    hanich_gitlab_host: str
    hanich_gitlab_token: str

    tests_repository_url: str
    tests_repository_ref: str

    hive_host: HttpUrl
    hive_api_user: str
    hive_api_pass: str

    hive_input_json_path: Path = Path("/mnt/autocheck/input.json'")
    hive_output_json_path: Path = Path("/mnt/autocheck/output.json'")

    logging_level: str = "WARNING"


settings = Settings()
