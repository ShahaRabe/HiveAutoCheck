import base64

from pathlib import Path
import pytest
import patoolib
from autocheck.exercise import Exercise
from autocheck.input_json import InputJSON
from autocheck.autocheck import write_output

from typing import Generator


@pytest.fixture(scope="session")
def __save_input_file(input_json: InputJSON, original_file_path: Path | None) -> None:
    if not original_file_path or not input_json.file:
        return

    original_file_path.parent.mkdir(parents=True, exist_ok=True)

    content = base64.b64decode(input_json.file)
    original_file_path.write_bytes(content)


@pytest.fixture(scope="session")
def __extract_file_to_disk(
    original_file_path: Path, extracted_path: Path | None, __save_input_file: None
) -> None:
    if not extracted_path:
        # Not an archive or no file submitted
        return

    extracted_path.mkdir(parents=True, exist_ok=True)
    patoolib.extract_archive(str(original_file_path), outdir=str(extracted_path))


@pytest.fixture(scope="session", autouse=True)
def __setup_teardown(
    __extract_file_to_disk: None, exercise: Exercise
) -> Generator[None, None, None]:
    yield
    write_output(exercise)
