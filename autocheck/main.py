import os
import pytest

from exercise import Exercise, FieldType
from conftest import get_exercise, get_submitted_file, ORIGINAL_SUBMITTED_FILE_PATH
from autocheck import AutocheckResponse, ContentDescriptor, ResponseType
from autocheck import InputOutputJson


def save_and_unpack_attached_file():
    file_content = get_submitted_file()
    os.makedirs(ORIGINAL_SUBMITTED_FILE_PATH, exist_ok=True)
    with open(ORIGINAL_SUBMITTED_FILE_PATH / InputOutputJson.file_name(), 'wb') as input_file:
        input_file.write(file_content)


def main():
    save_and_unpack_attached_file()

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
