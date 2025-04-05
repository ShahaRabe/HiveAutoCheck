import json
import logging
from pathlib import Path

import pytest

from autocheck.hive import HiveAPI

from .exercise import Exercise
from .fixtures import TESTS_FILES_DIRECTORY, get_input_json
from .gitlab_client.gitlab_client import GitlabClient
from .settings import settings


def clone_tests_repository(
    gitlab_host: str, gitlab_token: str, repository_url: str, repository_ref: str
) -> None:
    segel_gitlab_client = GitlabClient(gitlab_host, gitlab_token)
    segel_gitlab_client.clone(repository_url, TESTS_FILES_DIRECTORY, repository_ref)


def get_tests_to_run(exercise: Exercise) -> list[str]:
    exercise_relative_path: Path = Path(exercise.subject_name) / exercise.module_name
    metadata_file_path = (
        TESTS_FILES_DIRECTORY / "metadata" / exercise_relative_path / "tests_list.json"
    )

    with metadata_file_path.open() as metadata_file:
        return [
            str(TESTS_FILES_DIRECTORY / test)
            for test in json.load(metadata_file)[exercise.name]
        ]


def main() -> None:
    logging.basicConfig(level=int(getattr(logging, settings.logging_level)))

    clone_tests_repository(
        settings.segel_gitlab_host,
        settings.segel_gitlab_token,
        settings.tests_repository_url,
        settings.tests_repository_ref,
    )

    input_json = get_input_json()

    hive_client = HiveAPI(
        str(settings.hive_host), settings.hive_api_user, settings.hive_api_pass
    )

    exercise = hive_client.get_exercise_by_assignment_id(input_json.assignment_id)
    tests = get_tests_to_run(exercise)
    pytest.main(["--rootdir", str(TESTS_FILES_DIRECTORY), "-o", "log_cli=1"] + tests)


if __name__ == "__main__":
    main()
