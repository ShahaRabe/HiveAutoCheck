import os
from typing import Dict, List

import requests
import urllib3

from urllib3.exceptions import InsecureRequestWarning

from .exercise import Exercise, Field, FieldType

urllib3.disable_warnings(InsecureRequestWarning)


class HiveAPI:
    def __init__(self):
        username = os.environ.get('HIVE_API_USER')
        password = os.environ.get('HIVE_API_PASS')
        hive_host = os.environ.get('HIVE_HOST')

        assert username is not None and \
               password is not None and \
               hive_host is not None and hive_host.lower().startswith('http')

        self.hive_host = hive_host
        self.session = requests.session()
        self.token = self.login(username, password)
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def _get_api_response(self, api: str) -> requests.Response:
        return self.session.get(self.hive_host + api, headers=self.headers, verify=False)

    def login(self, username: str, password: str) -> str:
        """
        Login to server
        @param username: The username to log in with
        @param password: The password to log in with
        """
        cred: Dict[str, str] = {"username": username, "password": password}
        response = self.session.get(self.hive_host + "/api/auth/session", verify=False)
        if response.status_code != 200:
            raise RuntimeError("Failed to login to hive!")

        response = self.session.post(self.hive_host + "/api/core/token/", json=cred, verify=False)
        if response.status_code != 200:
            raise RuntimeError("Failed to get token!")

        return response.json()["access"]

    def get_exercise_id_by_assignment_id(self, assignemnt_id: int) -> int:
        response = self._get_api_response(f"/api/core/assignments/{assignemnt_id}")

        try:
            return response.json()["exercise"]
        except IndexError as ex:
            raise RuntimeError(f"assignment {assignemnt_id} does not exist") from ex

    def retrieve_exercise_fields_by_id(self, exercise_id) -> List[Field]:
        response = self._get_api_response(f"/api/core/course/exercises/{exercise_id}/fields/")
        fields = response.json()
        return [
            Field(field["id"],
                  field["name"],
                  field["has_value"],
                  FieldType(field['type'])) for field in fields
        ]

    def get_exercise_by_id(self, exercise_id: int) -> Exercise:
        response = self._get_api_response(f"/api/core/course/exercises/{exercise_id}")
        try:
            resp_json = response.json()
            return Exercise(exercise_id,
                            resp_json["name"],
                            resp_json["parent_module_name"],
                            resp_json["parent_subject_symbol"],
                            resp_json["parent_subject_name"],
                            self.retrieve_exercise_fields_by_id(exercise_id))
        except IndexError as ex:
            raise RuntimeError(f"exercise {exercise_id} does not exist") from ex
