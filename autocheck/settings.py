from enum import StrEnum, auto
from pathlib import Path
from typing import Annotated

from pydantic import HttpUrl, StringConstraints
from pydantic_settings import BaseSettings


class HanichRepositoryBranchType(StrEnum):
    WORK = auto()
    BASE = auto()


class Settings(BaseSettings):
    segel_gitlab_host: str
    segel_gitlab_token: str

    hanich_gitlab_host: str
    hanich_gitlab_token: str

    tests_repository_url: str
    tests_repository_ref: str

    hive_url: HttpUrl

    hive_input_json_path: Path = Path("/mnt/autocheck/input.json")
    hive_output_json_path: Path = Path("/mnt/autocheck/output.json")

    hanich_repository_url_exercise_field_name: str = "repository_url"
    hanich_repository_branch_name: str = "dev"
    hanich_repository_branch_type: HanichRepositoryBranchType | None = None
    """If set, the branch name will be taken from `on_creation_data` according to the type"""

    logging_level: Annotated[str, StringConstraints(to_upper=True)] = "WARNING"


settings = Settings()
