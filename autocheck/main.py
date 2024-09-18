import os

from hive import HiveAPI
from exercise import Exercise
from autocheck import InputOutputJson, ResponseType, ContentDescriptor

USERNAME = os.environ.get('API_USER')
PASSWORD = os.environ.get('API_PASS')
HIVE_HOST = os.environ.get('HIVE_HOST')


def main():
    hive: HiveAPI = HiveAPI(USERNAME, PASSWORD, HIVE_HOST)
    response = InputOutputJson.input_json()

    exercise_id: int = hive.get_exercise_id_by_assignment_id(response["assignment_id"])
    exercise: Exercise = hive.get_exercise_by_id(exercise_id)

    exercise_string_id = f"{exercise.subject_letter}_{exercise.subject_name}/{exercise.module_name}/{exercise.name}"                                   

    InputOutputJson.write_output(exercise,
                                [ ContentDescriptor(exercise_string_id, "Comment") ],
                                ResponseType.AutoCheck,
                                segel_only=True,
                                hide_checker_name=True)


if __name__ == '__main__':
    main()
