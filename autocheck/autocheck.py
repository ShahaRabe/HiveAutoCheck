import json
import base64
import os

from dataclasses import dataclass
from typing import List, Dict, Union, Any
from enum import IntEnum
from pathlib import Path

from exercise import Exercise


class ResponseType(IntEnum):
    AutoCheck = 1
    Done = 2
    Redo = 3


@dataclass
class ContentDescriptor:
    content: str
    field_name: str


@dataclass
class AutocheckResponse:
    content_descriptors: List[ContentDescriptor]
    response_type: ResponseType
    segel_only: bool = True
    hide_checker_name: bool = True


class InputOutputJson:
    __test_responses: Dict[str, AutocheckResponse] = {}
    @staticmethod
    def input_json() -> Dict[str, Any]:
        with open('/mnt/autocheck/input.json', 'r', encoding='utf-8') as input_file:
            return json.load(input_file)


    @staticmethod
    def file_name() -> str:
        return InputOutputJson.input_json()['file_name']


    @staticmethod
    def save_input_file_if_exists(dirname: Path) -> None:
        file_name = InputOutputJson.file_name()
        if not file_name:
            return

        os.makedirs(dirname, exist_ok=True)

        content = base64.b64decode(InputOutputJson.input_json()['file'])
        file_path = dirname / file_name
        file_path.write_bytes(content)


    @staticmethod
    def add_response(function: str, response: AutocheckResponse) -> None:
        InputOutputJson.__test_responses[function] = response


    HiveFieldContentDict = Dict[str, Union[int, str]]
    @staticmethod
    def _get_contents_array(exercise: Exercise) -> List[HiveFieldContentDict]:
        contents_by_field: Dict[int, List[str]] = {}
        for test, response in InputOutputJson.__test_responses.items():
            for desc in response.content_descriptors:
                field_id: int = exercise.get_field_id(desc.field_name)
                if field_id not in contents_by_field:
                    contents_by_field[field_id] = []

                contents_by_field[field_id].append(f'### {test}:\n{desc.content}')

        return [
            {
                "field": field_id,
                "content": '\n\n'.join(field_contents)
            } for field_id, field_contents in contents_by_field.items()
        ]


    @staticmethod
    def write_output(exercise: Exercise) -> None:
        current_segel_only = (resp.segel_only for resp in InputOutputJson.__test_responses.values())
        current_response_types = \
            (resp.response_type.value for resp in InputOutputJson.__test_responses.values())
        current_checker_name =\
            (resp.hide_checker_name for resp in InputOutputJson.__test_responses.values())

        response_type: ResponseType = ResponseType(max(current_response_types))
        segel_only: bool = any(current_segel_only)
        hide_checker_name: bool = any(current_checker_name)

        data = {
            "contents": InputOutputJson._get_contents_array(exercise),
            "type": response_type.name,
            "segel_only": segel_only,
            "hide_checker_name": hide_checker_name,
        }

        with open('/mnt/autocheck/output.json', 'w', encoding='utf-8') as output_file:
            json.dump(data, output_file)
