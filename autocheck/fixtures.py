import json
import os.path
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

import patoolib
import pytest

from .BlackboxTests.blackbox_test_config import BlackboxTestConfig
from .compiler.cmake_compiler import CMakeCompiler
from .compiler.compiler import Compiler
from .compiler.exceptions import CompilationException
from .compiler.make_compiler import MakeCompiler
from .exercise import Exercise
from .gitlab_client.gitlab_client import GitlabClient
from .hive import HiveAPI
from .input_json import InputJSON
from .settings import settings

__ORIGINAL_FILE_DIRECTORY: Path = Path("/tmp/exercise_files/original")
TESTS_FILES_DIRECTORY: Path = (
    Path(os.path.dirname(os.path.realpath(__file__))) / "test_files"
)


def get_input_file() -> InputJSON:
    with open(settings.hive_input_json_path, encoding="utf-8") as input_file:
        content: dict[str, Any] = json.load(input_file)
        return InputJSON(**content)


@pytest.fixture(scope="session")
def input_json() -> InputJSON:
    return get_input_file()


def get_exercise_from_input(input_json: InputJSON) -> Exercise:
    hive = HiveAPI(
        str(settings.hive_host), settings.hive_api_user, settings.hive_api_pass
    )
    exercise_id: int = hive.get_exercise_id_by_assignment_id(input_json.assignment_id)
    return hive.get_exercise_by_id(exercise_id)


@pytest.fixture(scope="session")
def exercise(input_json: InputJSON) -> Exercise:
    return get_exercise_from_input(input_json)


@pytest.fixture(scope="session")
def original_file_path(input_json: InputJSON) -> Path | None:
    file_name = input_json.file_name
    if not file_name:
        return None

    return __ORIGINAL_FILE_DIRECTORY / file_name


@pytest.fixture(scope="session")
def submitted_repository_url(input_json: InputJSON) -> str | None:
    return input_json.get_field_content("repository_url")


@pytest.fixture(scope="session")
def hanich_gitlab_client() -> GitlabClient:
    return GitlabClient(settings.hanich_gitlab_host, settings.hanich_gitlab_token)


@pytest.fixture(scope="session")
def temp_directory() -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture(scope="session")
def cloned_repository(
    hanich_gitlab_client: GitlabClient,
    submitted_repository_url: str,
    temp_directory: Path,
) -> Path:
    hanich_gitlab_client.clone(submitted_repository_url, temp_directory, "main")
    return temp_directory


def compile_and_get_executable_path(
    cloned_repository: Path, exercise: Exercise, compiler_type: type[Compiler]
) -> Path:
    result, out, err = compiler_type.compile(cloned_repository, exercise.name)

    if result == 0:
        return compiler_type.find_executable_path(cloned_repository, exercise.name)

    if err:
        raise CompilationException(f"Solution build failed:\n{err.decode()}")
    raise CompilationException(f"Solution build failed:\n{out.decode()}")


@pytest.fixture(scope="session")
def make_compiled_executable(cloned_repository: Path, exercise: Exercise) -> Path:
    return compile_and_get_executable_path(cloned_repository, exercise, MakeCompiler)


@pytest.fixture(scope="session")
def cmake_compiled_executable(cloned_repository: Path, exercise: Exercise) -> Path:
    return compile_and_get_executable_path(cloned_repository, exercise, CMakeCompiler)


@pytest.fixture(scope="session")
def blackbox_test_configs(exercise: Exercise) -> list[BlackboxTestConfig]:
    module_name: str = (
        exercise.name.replace(" ", "_").replace(".", "_").replace("'", "").lower()
    )

    test_file_path: Path = (
        Path("test_configs") / exercise.subject_name / "config" / module_name
    )
    return BlackboxTestConfig.load_config_from_file(test_file_path)


@pytest.fixture(scope="session")
def submitted_file(original_file_path: Path | None) -> bytes | None:
    file_path: Path = original_file_path or Path()
    if not file_path.is_file():
        return None

    return file_path.read_bytes()


@pytest.fixture(scope="session")
def extracted_path(original_file_path: Path | None) -> Path | None:
    original_file = original_file_path or Path()
    if not patoolib.is_archive(original_file):
        return None

    return Path("/tmp/exercise_files/unpacked")
