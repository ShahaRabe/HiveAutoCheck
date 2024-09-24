import os

import pytest
import patoolib

from exercise import Exercise, FieldType
from conftest import get_exercise, \
                     get_submitted_file, \
                     get_original_file_path, \
                     ORIGINAL_SUBMITTED_FILE_PATH, \
                     EXTRACTED_FILE_PATH

from autocheck import AutocheckResponse, ContentDescriptor, ResponseType
from autocheck import InputOutputJson


def save_attached_file() -> None:
    file_content = get_submitted_file()
    os.makedirs(ORIGINAL_SUBMITTED_FILE_PATH, exist_ok=True)

    with get_original_file_path().open('wb') as input_file:
        input_file.write(file_content)


def extract_file_to_disk() -> None:
    patoolib.extract_archive(str(get_original_file_path()), outdir=str(EXTRACTED_FILE_PATH))


def setup_environment() -> None:
    save_attached_file()
    extract_file_to_disk()


def main():
    setup_environment()

    exit_code = pytest.main([])
    exercise: Exercise = get_exercise()

    if exit_code != 0:
        framework_error_message = '''One or more of your autochecks failed!
please see autocheck logs for more info...'''

        contents = [
            ContentDescriptor(framework_error_message, field.name)
            for field in exercise.fields if field.has_value and field.type == FieldType.Text
        ]

        InputOutputJson.add_response('Hive-Tester-Framework',
                                     AutocheckResponse(contents,
                                                       ResponseType.Redo,
                                                       segel_only=True))

    InputOutputJson.write_output(exercise)


if __name__ == '__main__':
    main()
