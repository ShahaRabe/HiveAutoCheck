from typing import List
import os

import pytest

from .conftest import TESTS_FILES_DIRECTORY, get_input_file, get_exercise_from_input, get_tests_to_run
from .exercise import Exercise
from .input_json import InputJSON
from .gitlab_client.gitlab_client import GitlabClient


def clone_tests_config() -> None:
    segel_gitlab_host = os.getenv('SEGEL_GITLAB_HOST')
    segel_gitlab_token = os.getenv('SEGEL_GITLAB_TOKEN')
    segel_gitlab_client = GitlabClient(segel_gitlab_host, segel_gitlab_token)

    tests_repo_url = os.getenv('TESTS_REPOSITORY_URL')
    segel_gitlab_client.clone(tests_repo_url, TESTS_FILES_DIRECTORY, 'main')


def main():
    clone_tests_config()

    input_json_file: InputJSON = get_input_file()
    exercise_data: Exercise = get_exercise_from_input(input_json_file)
    tests: List[str] = get_tests_to_run(exercise_data)
    pytest.main(tests)


if __name__ == '__main__':
    main()
