import json
import logging
from pathlib import Path

import pytest

from .exercise import Exercise
from .fixtures import TESTS_FILES_DIRECTORY, get_exercise_from_input, get_input_file
from .gitlab_client.gitlab_client import GitlabClient
from .input_json import InputJSON
from .settings import settings


def clone_tests_repository(
    gitlab_host: str, gitlab_token: str, repository_url: str, repository_ref: str
) -> None:
    segel_gitlab_client = GitlabClient(gitlab_host, gitlab_token)
    segel_gitlab_client.clone(repository_url, TESTS_FILES_DIRECTORY, repository_ref)


def get_tests_to_run(exercise: Exercise) -> list[str]:
    exercise_relative_path: Path = Path(exercise.subject_name) / exercise.module_name
    metadata_file_path: Path = (
        TESTS_FILES_DIRECTORY / "metadata" / exercise_relative_path / "tests_list.json"
    )

    with open(metadata_file_path) as f:
        return [
            str(TESTS_FILES_DIRECTORY / test) for test in json.load(f)[exercise.name]
        ]


def main() -> None:
    logging.basicConfig(level=int(getattr(logging, settings.logging_level)))

    clone_tests_repository(
        settings.segel_gitlab_host,
        settings.segel_gitlab_token,
        settings.tests_repository_url,
        settings.tests_repository_ref,
    )

    input_json_file: InputJSON = get_input_file()
    exercise_data: Exercise = get_exercise_from_input(input_json_file)
    tests: list[str] = get_tests_to_run(exercise_data)
    pytest.main(["--rootdir", str(TESTS_FILES_DIRECTORY), "-o", "log_cli=1"] + tests)


if __name__ == "__main__":
    main()
