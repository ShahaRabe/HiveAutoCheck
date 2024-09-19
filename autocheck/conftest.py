import pytest

from autocheck import InputOutputJson
from hive import HiveAPI
from exercise import Exercise


def get_exercise() -> Exercise:
    hive: HiveAPI = HiveAPI()
    response = InputOutputJson.input_json()

    exercise_id: int = hive.get_exercise_id_by_assignment_id(response["assignment_id"])
    return hive.get_exercise_by_id(exercise_id)


@pytest.fixture
def exercise() -> Exercise:
    return get_exercise()
