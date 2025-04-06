import base64
from collections.abc import Generator
from pathlib import Path

import patoolib
import pytest

from autocheck.autocheck import write_output
from autocheck.exercise import Exercise
from autocheck.input import AutocheckInput


@pytest.fixture(scope="session")
def _save_input_file(
    autocheck_input: AutocheckInput,
    original_file_path: Path | None,
) -> None:
    if not original_file_path or not autocheck_input.file:
        return

    original_file_path.parent.mkdir(parents=True, exist_ok=True)

    content = base64.b64decode(autocheck_input.file)
    original_file_path.write_bytes(content)


@pytest.fixture(scope="session")
def _extract_file_to_disk(
    original_file_path: Path,
    extracted_path: Path | None,
    _save_input_file: None,
) -> None:
    if not extracted_path:
        # Not an archive or no file submitted
        return

    extracted_path.mkdir(parents=True, exist_ok=True)
    patoolib.extract_archive(str(original_file_path), outdir=str(extracted_path))


@pytest.fixture(scope="session", autouse=True)
def _setup_teardown(
    _extract_file_to_disk: None,
    exercise: Exercise,
) -> Generator[None, None, None]:
    yield
    write_output(exercise)
