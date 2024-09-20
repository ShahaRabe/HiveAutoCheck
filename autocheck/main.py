import pytest

from autocheck import AutocheckResponse, ContentDescriptor, ResponseType
from autocheck import InputOutputJson
from conftest import get_exercise
from exercise import Exercise


def main():
    exit_code = pytest.main([])
    exercise: Exercise = get_exercise()
    
    if exit_code != 0:
        contents = [ContentDescriptor('One or more of your autochecks failed!\nplease see autocheck logs for more info...', field.name) for field in exercise.fields]
        InputOutputJson.add_response('Hive-Tester-Framework', AutocheckResponse(contents, ResponseType.Redo, segel_only=True))

    InputOutputJson.write_output(exercise)


if __name__ == '__main__':
    main()
