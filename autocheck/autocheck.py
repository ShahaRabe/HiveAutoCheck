import json

from dataclasses import dataclass
from typing import List, Dict
from enum import IntEnum

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


_test_responses: Dict[str, AutocheckResponse] = {}


class InputOutputJson:
    @staticmethod
    def input_json():
        with open('/mnt/autocheck/input.json', 'r') as input_file:
            return json.load(input_file)
    

    @staticmethod
    def add_response(function: str, response: AutocheckResponse) -> None:
        global _test_responses
        _test_responses[function] = response
    

    @staticmethod
    def _get_contents_array(exercise: Exercise):
        global _test_responses

        contents_by_field: Dict[int, List[str]] = {}
        for test, response in _test_responses.items():
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
        global _test_responses
        
        response_type: ResponseType = ResponseType(max([resp.response_type.value for resp in _test_responses.values()]))
        segel_only: bool = any([resp.segel_only for resp in _test_responses.values()])
        hide_checker_name: bool = any([resp.hide_checker_name for resp in _test_responses.values()])

        data = {
            "contents": InputOutputJson._get_contents_array(exercise),
            "type": response_type.name,
            "segel_only": segel_only,
            "hide_checker_name": hide_checker_name,
        }

        with open('/mnt/autocheck/output.json', 'w') as output_file:
            json.dump(data, output_file)
