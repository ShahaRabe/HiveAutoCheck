import os

from pathlib import Path
from typing import Optional

import pytest
import patoolib

from hive import HiveAPI
from exercise import Exercise
from autocheck import InputOutputJson


__ORIGINAL_FILE_DIRECTORY: Path = Path('/tmp/exercise_files/original')


def get_exercise() -> Exercise:
    hive: HiveAPI = HiveAPI()
    response = InputOutputJson.input_json()

    exercise_id: int = hive.get_exercise_id_by_assignment_id(response["assignment_id"])
    return hive.get_exercise_by_id(exercise_id)


@pytest.fixture
def exercise() -> Exercise:
    return get_exercise()


def get_original_file_path() -> Optional[Path]:
    file_path = __ORIGINAL_FILE_DIRECTORY / InputOutputJson.file_name()
    if not file_path.is_file():
        return None

    return file_path


@pytest.fixture
def original_file_path() -> Optional[Path]:
    return get_original_file_path()


@pytest.fixture
def submitted_file() -> Optional[bytes]:
    file_path: Path = get_original_file_path() or Path()
    if not file_path.is_file():
        return None

    return file_path.read_bytes()


def get_extracted_path() -> Optional[Path]:
    original_file = get_original_file_path() or Path()
    if not patoolib.is_archive(original_file):
        return None

    return Path('/tmp/exercise_files/unpacked')


@pytest.fixture
def extracted_path() -> Optional[Path]:
    return get_extracted_path()


def __extract_file_to_disk() -> None:
    out_path: Optional[Path] = get_extracted_path()
    if not out_path:
        # Not an archive or no file submitted
        return

    os.makedirs(out_path, exist_ok=True)
    patoolib.extract_archive(str(get_original_file_path()), outdir=str(out_path))


def setup_environment() -> None:
    InputOutputJson.save_input_file_if_exists(__ORIGINAL_FILE_DIRECTORY)
    __extract_file_to_disk()
