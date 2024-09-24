import base64

from pathlib import Path

import pytest

from hive import HiveAPI
from exercise import Exercise
from autocheck import InputOutputJson


ORIGINAL_SUBMITTED_FILE_PATH: Path = Path('/tmp/exercise_files/original')
EXTRACTED_FILE_PATH: Path = Path('/tmp/exercise_files/unpacked')


def get_exercise() -> Exercise:
    hive: HiveAPI = HiveAPI()
    response = InputOutputJson.input_json()

    exercise_id: int = hive.get_exercise_id_by_assignment_id(response["assignment_id"])
    return hive.get_exercise_by_id(exercise_id)


@pytest.fixture
def exercise() -> Exercise:
    return get_exercise()


def get_submitted_file() -> bytes:
    return base64.b64decode(InputOutputJson.input_json()['file'])


@pytest.fixture
def submitted_file() -> bytes:
    return get_submitted_file()


def get_original_file_path() -> Path:
    return ORIGINAL_SUBMITTED_FILE_PATH / InputOutputJson.file_name()


@pytest.fixture
def original_file_path() -> Path:
    return get_original_file_path()


@pytest.fixture
def extracted_files_path() -> Path:
    return EXTRACTED_FILE_PATH
