import os
import requests

from typing import Dict, List
import urllib3
from urllib3.exceptions import InsecureRequestWarning

from exercise import Exercise, Field

urllib3.disable_warnings(InsecureRequestWarning)


class HiveAPI:
    def __init__(self):
        USERNAME = os.environ.get('API_USER')
        PASSWORD = os.environ.get('API_PASS')
        HIVE_HOST = os.environ.get('HIVE_HOST')

        assert USERNAME is not None and \
               PASSWORD is not None and \
               HIVE_HOST is not None and HIVE_HOST.lower().startswith('http')    

        self.hive_host = HIVE_HOST
        self.session = requests.session()
        self.token = self.login(USERNAME, PASSWORD)
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def login(self, username: str, password: str) -> str:
        """
        Login to server
        @param username: The username to log in with
        @param password: The password to log in with
        """
        cred: Dict[str, str] = {"username": username, "password": password}
        response = self.session.get(self.hive_host + "/api/auth/session", verify=False)
        if response.status_code != 200:
            raise Exception("Failed to login to hive!")
        
        response = self.session.post(self.hive_host + "/api/core/token/", json=cred, verify=False)
        if response.status_code != 200:
            raise Exception("Failed to get token!")
        
        return response.json()["access"]


    def get_exercise_id_by_assignment_id(self, assignemnt_id: int) -> int:
        response = self.session.get(self.hive_host + "/api/core/assignments/{}".format(assignemnt_id),
                                    headers=self.headers,
                                    verify=False)
        try:
            return response.json()["exercise"]
        except IndexError:
            raise Exception(f"assignment {assignemnt_id} does not exist")


    def retrieve_exercise_fields_by_id(self, exercise_id) -> List[Field]:
        response = self.session.get(self.hive_host + "/api/core/course/exercise/{}/fields/".format(str(exercise_id)),
                                    headers=self.headers,
                                    verify=False)
        fields = response.json()
        return [Field(field["id"], field["name"], field["has_value"]) for field in fields]


    def get_exercise_by_id(self, exercise_id: int) -> Exercise:
        response = self.session.get(self.hive_host + "/api/core/course/exercises/{}".format(exercise_id),
                                    headers=self.headers,
                                    verify=False)
        try:
            resp_json = response.json()
            return Exercise(exercise_id,
                            resp_json["name"],
                            resp_json["parent_module_name"],
                            resp_json["parent_subject_symbol"],
                            resp_json["parent_subject_name"],
                            self.retrieve_exercise_fields_by_id(exercise_id))
        except IndexError:
            raise Exception(f"exercise {exercise_id} does not exist")
    