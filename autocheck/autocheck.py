import json

from dataclasses import dataclass
from typing import List
from enum import Enum

from exercise import Exercise


class ResponseType(Enum):
    AutoCheck = 1
    Redo = 2
    Done = 3


@dataclass
class ContentDescriptor:
    content: str
    field_name: str


class InputOutputJson:
    @staticmethod
    def input_json():
        with open('/mnt/autocheck/input.json', 'r') as input_file:
            return json.load(input_file)
    

    @staticmethod
    def write_output(exercise: Exercise,
                     content_descriptors: List[ContentDescriptor],
                     response_type: ResponseType,
                     segel_only: bool,
                     hide_checker_name: bool) -> None:
        contents = [
            {
                "content": desc.content,
                "field": exercise.get_field_id(desc.field_name)
            } for desc in content_descriptors
        ]
        
        data = {
            "contents": contents,
            "type": response_type.name,
            "segel_only": segel_only,
            "hide_checker_name": hide_checker_name,
        }

        with open('/mnt/autocheck/output.json', 'w') as output_file:
            json.dump(data, output_file)
