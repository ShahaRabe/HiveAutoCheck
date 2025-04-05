import logging

import pytest

from autocheck.fixtures import (
    TESTS_FILES_DIRECTORY,
    get_autocheck_input,
    get_exercise_test_metadata,
)
from autocheck.gitlab_client.gitlab_client import GitlabClient
from autocheck.hive import HiveClient
from autocheck.settings import settings


def clone_tests_repository(
    gitlab_host: str,
    gitlab_token: str,
    repository_url: str,
    repository_ref: str,
) -> None:
    segel_gitlab_client = GitlabClient(gitlab_host, gitlab_token)
    segel_gitlab_client.clone(repository_url, TESTS_FILES_DIRECTORY, repository_ref)


def main() -> None:
    logging.basicConfig(level=int(getattr(logging, settings.logging_level)))

    clone_tests_repository(
        settings.segel_gitlab_host,
        settings.segel_gitlab_token,
        settings.tests_repository_url,
        settings.tests_repository_ref,
    )

    autocheck_input = get_autocheck_input()
    exercise = HiveClient(settings.hive_url).get_exercise_by_assignment_id(
        autocheck_input.assignment_id,
    )

    exercise_test_metadata = get_exercise_test_metadata(exercise)
    tests = [str(TESTS_FILES_DIRECTORY / test) for test in exercise_test_metadata.tests]

    pytest.main(["--rootdir", str(TESTS_FILES_DIRECTORY), "-o", "log_cli=1", *tests])


if __name__ == "__main__":
    main()
