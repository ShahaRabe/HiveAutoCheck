from typing import List

import pytest

from conftest import get_input_file, get_exercise_from_input, get_tests_to_run
from exercise import Exercise
from input_json import InputJSON


def main():
    input_json_file: InputJSON = get_input_file()
    exercise_data: Exercise = get_exercise_from_input(input_json_file)
    tests: List[str] = get_tests_to_run(exercise_data)
    pytest.main(tests)


if __name__ == '__main__':
    main()
