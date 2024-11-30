from pathlib import Path
from typing import Optional, Generator, Dict, Any

import base64
import json
import patoolib
import pytest

from hive import HiveAPI
from exercise import Exercise
from autocheck import write_output


__ORIGINAL_FILE_DIRECTORY: Path = Path('/tmp/exercise_files/original')


@pytest.fixture(scope='session')
def input_json() -> Dict[str, Any]:
    with open('/mnt/autocheck/input.json', 'r', encoding='utf-8') as input_file:
        return json.load(input_file)


@pytest.fixture(scope='session')
def exercise(input_json: Dict[str, Any]) -> Exercise:
    hive: HiveAPI = HiveAPI()
    exercise_id: int = hive.get_exercise_id_by_assignment_id(input_json["assignment_id"])
    return hive.get_exercise_by_id(exercise_id)


@pytest.fixture(scope='session')
def original_file_path(input_json: Dict[str, Any]) -> Optional[Path]:
    file_name = input_json['file_name']
    if not file_name:
        return None

    return __ORIGINAL_FILE_DIRECTORY / file_name


@pytest.fixture(scope='session')
def submitted_file(original_file_path: Optional[Path]) -> Optional[bytes]:
    file_path: Path = original_file_path or Path()
    if not file_path.is_file():
        return None

    return file_path.read_bytes()


@pytest.fixture(scope='session')
def extracted_path(original_file_path: Optional[Path]) -> Optional[Path]:
    original_file = original_file_path or Path()
    if not patoolib.is_archive(original_file):
        return None

    return Path('/tmp/exercise_files/unpacked')


@pytest.fixture(scope='session')
def __save_input_file(input_json: Dict[str, Any], original_file_path: Optional[Path]) -> None:
    if not original_file_path:
        return

    original_file_path.parent.mkdir(parents=True, exist_ok=True)

    content = base64.b64decode(input_json['file'])
    original_file_path.write_bytes(content)


@pytest.fixture(scope='session')
def __extract_file_to_disk(original_file_path: Path,
                           extracted_path: Optional[Path],
                           __save_input_file: None) -> None:
    if not extracted_path:
        # Not an archive or no file submitted
        return

    extracted_path.mkdir(parents=True, exist_ok=True)
    patoolib.extract_archive(str(original_file_path), outdir=str(extracted_path))


@pytest.fixture(scope='session', autouse=True)
def __setup_teardown(__extract_file_to_disk: None, exercise: Exercise) -> Generator:
    yield
    write_output(exercise)
