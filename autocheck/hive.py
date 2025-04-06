from http import HTTPStatus

import requests
import urllib3
from pydantic import HttpUrl
from urllib3.exceptions import InsecureRequestWarning

from .assignment import Assignment
from .exercise import Exercise, ExerciseField

urllib3.disable_warnings(InsecureRequestWarning)


class HiveClient:
    def __init__(self, url: HttpUrl) -> None:
        self.host = f"{url.scheme}://{url.host}:{url.port}"
        self.session = requests.session()
        if not url.username or not url.password:
            raise ValueError(
                "Please specify Hive's autocheck API credentials (e.g. https://<user>:<password>:<host>)",
            )
        self.token = self.login(url.username, url.password)
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def _get_api_response(self, api: str) -> requests.Response:
        return self.session.get(self.host + api, headers=self.headers, verify=False)

    def login(self, username: str, password: str) -> str:
        cred: dict[str, str] = {"username": username, "password": password}
        response = self.session.get(self.host + "/api/auth/session", verify=False)
        if response.status_code != HTTPStatus.OK:
            raise RuntimeError("Failed to login to hive!")

        response = self.session.post(
            self.host + "/api/core/token/",
            json=cred,
            verify=False,
        )
        if response.status_code != HTTPStatus.OK:
            raise RuntimeError("Failed to get token!")

        return str(response.json()["access"])

    def get_assignment_by_id(self, assignment_id: int) -> Assignment:
        response = self._get_api_response(f"/api/core/assignments/{assignment_id}")
        response.raise_for_status()
        return Assignment.model_validate(response.json())

    def retrieve_exercise_fields_by_id(self, exercise_id: int) -> list[ExerciseField]:
        response = self._get_api_response(
            f"/api/core/course/exercises/{exercise_id}/fields/",
        )
        fields = response.json()
        return [ExerciseField.model_validate(field) for field in fields]

    def get_exercise_by_id(self, exercise_id: int) -> Exercise:
        response = self._get_api_response(f"/api/core/course/exercises/{exercise_id}")
        response.raise_for_status()
        exercise_json = response.json()
        exercise_json["fields"] = self.retrieve_exercise_fields_by_id(exercise_id)
        return Exercise.model_validate(exercise_json)

    def get_exercise_by_assignment_id(self, assignment_id: int) -> Exercise:
        assignment = self.get_assignment_by_id(assignment_id)
        return self.get_exercise_by_id(assignment.exercise)
