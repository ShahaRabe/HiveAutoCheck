import json
import logging
import re
import tempfile
from collections.abc import Generator
from pathlib import Path

import patoolib
import pytest

from autocheck.assignment import Assignment
from autocheck.BlackboxTests.blackbox_test_config import BlackboxTestConfig
from autocheck.compiler.cmake_compiler import CMakeCompiler
from autocheck.compiler.compiler import Compiler
from autocheck.compiler.exceptions import CompilationError
from autocheck.compiler.make_compiler import MakeCompiler
from autocheck.exercise import Exercise
from autocheck.gitlab_client.gitlab_client import GitlabClient
from autocheck.hive import HiveClient
from autocheck.input import AutocheckInput
from autocheck.metadata import ExerciseTestMetadata
from autocheck.settings import HanichRepositoryBranchType, settings

logger = logging.getLogger(__name__)

_ORIGINAL_FILE_DIRECTORY = Path("/tmp/exercise_files/original")
TESTS_FILES_DIRECTORY = Path(__file__).resolve().parent / "test_files"


def get_autocheck_input() -> AutocheckInput:
    with settings.hive_input_json_path.open(encoding="utf-8") as input_file:
        return AutocheckInput.model_validate(json.load(input_file))


def get_exercise_test_metadata(exercise: Exercise) -> ExerciseTestMetadata:
    exercises_test_metadata_file_path = (
        TESTS_FILES_DIRECTORY
        / "metadata"
        / exercise.subject_name
        / exercise.module_name
        / "exercises.json"
    )

    with exercises_test_metadata_file_path.open() as file:
        return ExerciseTestMetadata.model_validate(json.load(file)[exercise.name])


@pytest.fixture(scope="session")
def autocheck_input() -> AutocheckInput:
    return get_autocheck_input()


@pytest.fixture(scope="session")
def hive_client() -> HiveClient:
    return HiveClient(settings.hive_url)


@pytest.fixture(scope="session")
def exercise(hive_client: HiveClient, autocheck_input: AutocheckInput) -> Exercise:
    return hive_client.get_exercise_by_assignment_id(autocheck_input.assignment_id)


@pytest.fixture(scope="session")
def exercise_test_metadata(exercise: Exercise) -> ExerciseTestMetadata:
    return get_exercise_test_metadata(exercise)


@pytest.fixture(scope="session")
def assignment(hive_client: HiveClient, autocheck_input: AutocheckInput) -> Assignment:
    return hive_client.get_assignment_by_id(autocheck_input.assignment_id)


@pytest.fixture(scope="session")
def original_file_path(autocheck_input: AutocheckInput) -> Path | None:
    file_name = autocheck_input.file_name
    if not file_name:
        return None

    return _ORIGINAL_FILE_DIRECTORY / file_name


@pytest.fixture(scope="session")
def hanich_repository_url(
    assignment: Assignment,
    autocheck_input: AutocheckInput,
) -> str | None:
    """Attempts to find the hanich's Git clone URL of the current assignment.

    Hive's Assignment Service places the URL inside the assignment's description,
    if the URL is not found there, we fall back to an exercise field that can
    be configured, if both are missing, we return None.

    We're parsing the description instead of building the URL on our own because we
    don't have access to the hanich's number and for future compatibility.
    """
    match = re.search(r"https://[^\s)]+\.git", assignment.description)
    if match:
        return match.group()

    logger.debug(
        f"No Git clone URL was found in the assignment's description, "
        f"falling back to an exercise field named "
        f"`{settings.hanich_repository_url_exercise_field_name}`",
    )
    return autocheck_input.get_field_content(
        settings.hanich_repository_url_exercise_field_name,
    )


@pytest.fixture(scope="session")
def hanich_gitlab_client() -> GitlabClient:
    return GitlabClient(settings.hanich_gitlab_host, settings.hanich_gitlab_token)


@pytest.fixture(scope="session")
def temp_directory() -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture(scope="session")
def hanich_repository_branch(
    exercise: Exercise, exercise_test_metadata: ExerciseTestMetadata,
) -> str:
    if (
        settings.hanich_repository_branch_type is not None
        and exercise.on_creation_data.gitlab is None
    ):
        raise ValueError(
            (
                "Hanich repository branch type is set while "
                "on_creation_data's gitlab field is missing"
            ),
        )

    match settings.hanich_repository_branch_type:
        case HanichRepositoryBranchType.WORK:
            branch_name = exercise.on_creation_data.gitlab.work_branch_name
        case HanichRepositoryBranchType.BASE:
            branch_name = exercise.on_creation_data.gitlab.base_branch_name
        case None:
            branch_name = settings.hanich_repository_branch_name
        case _:
            # This should be unreachable as Pydantic takes care of validation
            raise ValueError("Invalid `hanich_repository_branch_type` setting")

    if exercise_test_metadata.hanich_repository_branch_name is not None:
        branch_name = exercise_test_metadata.hanich_repository_branch_name

    return branch_name


@pytest.fixture(scope="session")
def cloned_repository(
    hanich_gitlab_client: GitlabClient,
    hanich_repository_url: str,
    temp_directory: Path,
    hanich_repository_branch: str,
) -> Path:
    hanich_gitlab_client.clone(
        hanich_repository_url, temp_directory, hanich_repository_branch,
    )
    return temp_directory


def compile_and_get_executable_path(
    cloned_repository: Path,
    exercise: Exercise,
    compiler_type: type[Compiler],
) -> Path:
    result, out, err = compiler_type.compile(cloned_repository, exercise.name)

    if result == 0:
        return compiler_type.find_executable_path(cloned_repository, exercise.name)

    if err:
        raise CompilationError(f"Solution build failed:\n{err.decode()}")
    raise CompilationError(f"Solution build failed:\n{out.decode()}")


@pytest.fixture(scope="session")
def make_compiled_executable(cloned_repository: Path, exercise: Exercise) -> Path:
    return compile_and_get_executable_path(cloned_repository, exercise, MakeCompiler)


@pytest.fixture(scope="session")
def cmake_compiled_executable(cloned_repository: Path, exercise: Exercise) -> Path:
    return compile_and_get_executable_path(cloned_repository, exercise, CMakeCompiler)


@pytest.fixture(scope="session")
def blackbox_test_configs(exercise: Exercise) -> list[BlackboxTestConfig]:
    module_name = (
        exercise.name.replace(" ", "_").replace(".", "_").replace("'", "").lower()
    )

    test_file_path = (
        Path("test_configs") / exercise.subject_name / "config" / module_name
    )
    return BlackboxTestConfig.load_config_from_file(test_file_path)


@pytest.fixture(scope="session")
def submitted_file(original_file_path: Path | None) -> bytes | None:
    file_path = original_file_path or Path()
    if not file_path.is_file():
        return None

    return file_path.read_bytes()


@pytest.fixture(scope="session")
def extracted_path(original_file_path: Path | None) -> Path | None:
    original_file = original_file_path or Path()
    if not patoolib.is_archive(str(original_file)):
        return None

    return Path("/tmp/exercise_files/unpacked")
