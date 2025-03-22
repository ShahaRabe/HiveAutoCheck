from typing import List
from pathlib import Path
import json
import os
import logging

import pytest

from .fixtures import TESTS_FILES_DIRECTORY, get_input_file, get_exercise_from_input
from .exercise import Exercise
from .input_json import InputJSON
from .gitlab_client.gitlab_client import GitlabClient


def logging_level() -> int:
    return getattr(logging, os.getenv('LOGGING_LEVEL') or 'WARNING')


def clone_tests_config() -> None:
    segel_gitlab_host = os.getenv('SEGEL_GITLAB_HOST')
    segel_gitlab_token = os.getenv('SEGEL_GITLAB_TOKEN')
    segel_gitlab_client = GitlabClient(segel_gitlab_host, segel_gitlab_token)

    tests_repo_url = os.getenv('TESTS_REPOSITORY_URL')
    tests_repo_ref = os.getenv('TESTS_REPOSITORY_REF')
    segel_gitlab_client.clone(tests_repo_url, TESTS_FILES_DIRECTORY, tests_repo_ref)


def get_tests_to_run(exercise: Exercise) -> List[str]:
    exercise_relative_path: Path = Path(exercise.subject_name) / exercise.module_name
    metadata_file_path: Path = TESTS_FILES_DIRECTORY / 'metadata' / exercise_relative_path / 'tests_list.json'

    with open(metadata_file_path, 'r') as f:
        return [str(TESTS_FILES_DIRECTORY / test) for test in json.load(f)[exercise.name]]


def main():
    logging.basicConfig(level=logging_level())

    clone_tests_config()

    input_json_file: InputJSON = get_input_file()
    exercise_data: Exercise = get_exercise_from_input(input_json_file)
    tests: List[str] = get_tests_to_run(exercise_data)
    pytest.main(["--rootdir", TESTS_FILES_DIRECTORY, "-o", "log_cli=1"] + tests)


if __name__ == '__main__':
    main()
