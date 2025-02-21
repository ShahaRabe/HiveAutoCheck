import base64
import json
import os.path
import tempfile
from pathlib import Path
from typing import Optional, Generator, Dict, Any, List

import patoolib
import pytest

from BlackboxTests.blackbox_test_config import BlackboxTestConfig
from autocheck import write_output
from exercise import Exercise
from gitlab_client.gitlab_client import GitlabClient
from hive import HiveAPI
from input_json import InputJSON

__ORIGINAL_FILE_DIRECTORY: Path = Path('/tmp/exercise_files/original')
__TESTS_FILES_DIRECTORY: Path = Path(os.path.dirname(os.path.realpath(__file__))) / 'test_files'


def get_tests_to_run(exercise: Exercise) -> List[str]:
    exercise_relative_path: Path = Path(exercise.subject_name) / exercise.module_name
    metadata_file_path: Path = __TESTS_FILES_DIRECTORY / 'metadata' / exercise_relative_path / 'tests_list.json'

    with open(metadata_file_path, 'r') as f:
        return json.load(f)[exercise.name]


def get_input_file() -> InputJSON:
    with open('/mnt/autocheck/input.json', 'r', encoding='utf-8') as input_file:
        content: Dict[str, Any] = json.load(input_file)
        return InputJSON(**content)


@pytest.fixture(scope='session')
def input_json() -> InputJSON:
    return get_input_file()


def get_exercise_from_input(input_json: InputJSON) -> Exercise:
    hive: HiveAPI = HiveAPI()
    exercise_id: int = hive.get_exercise_id_by_assignment_id(input_json.assignment_id)
    return hive.get_exercise_by_id(exercise_id)


@pytest.fixture(scope='session')
def exercise(input_json: InputJSON) -> Exercise:
    return get_exercise_from_input(input_json)


@pytest.fixture(scope='session')
def original_file_path(input_json: InputJSON) -> Optional[Path]:
    file_name = input_json.file_name
    if not file_name:
        return None

    return __ORIGINAL_FILE_DIRECTORY / file_name


@pytest.fixture(scope='session')
def submitted_repository_url(input_json: InputJSON) -> str:
    entry_id: int = [entry for entry in input_json.form_fields if entry['name'] == 'repository url'][0]['id']
    url: str = [entry for entry in input_json.contents if entry['field'] == entry_id][0]['content']
    return url



@pytest.fixture(scope='session')
def gitlab_client() -> GitlabClient:
    gitlab_token: str = os.getenv('GITLAB_TOKEN')
    gitlab_host: str = os.getenv('GITLAB_HOST')
    return GitlabClient(gitlab_host, gitlab_token)


@pytest.fixture(scope='session')
def temp_directory() -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture(scope='session')
def cloned_repository(gitlab_client: GitlabClient,
                      submitted_repository_url: str,
                      temp_directory: Path) -> Path:
    gitlab_client.clone(submitted_repository_url, temp_directory, "main")
    return temp_directory


@pytest.fixture(scope='session')
def blackbox_test_configs(exercise: Exercise) -> List[BlackboxTestConfig]:
    module_name: str = (exercise.name
                        .replace(' ', '_')
                        .replace('.', '_')
                        .replace('\'', '')
                        .lower())
    
    test_file_path: Path = Path('test_configs') / exercise.subject_name / 'config' / module_name
    return BlackboxTestConfig.load_config_from_file(test_file_path)


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
def __save_input_file(input_json: InputJSON, original_file_path: Optional[Path]) -> None:
    if not original_file_path:
        return

    original_file_path.parent.mkdir(parents=True, exist_ok=True)

    content = base64.b64decode(input_json.file)
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
