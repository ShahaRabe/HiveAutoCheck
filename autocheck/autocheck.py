import json

from dataclasses import dataclass
from typing import List, Dict, Union, Optional, Any
from enum import IntEnum, Enum
from functools import wraps, partial

from exercise import Exercise, FieldType


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


__test_responses: Dict[str, AutocheckResponse] = {}
HiveFieldContentDict = Dict[str, Union[int, str]]


def __get_contents_array(exercise: Exercise, segel_only: bool) -> List[HiveFieldContentDict]:
    contents_by_field: Dict[int, List[str]] = {}
    for test, response in __test_responses.items():
        if response.segel_only != segel_only:
            continue

        for desc in response.content_descriptors:
            field_names = []
            if desc.field_name is None:
                field_names = [
                    field.name
                    for field in exercise.fields if field.has_value and field.type == FieldType.Text
                ]
            else:
                field_names = [desc.field_name]

            for field_name in field_names:
                field_id: int = exercise.get_field_id(field_name)
                if field_id not in contents_by_field:
                    contents_by_field[field_id] = []

                contents_by_field[field_id].append(f'### {test}:\n{desc.content}')

    return [
        {
            "field": field_id,
            "content": '\n\n'.join(field_contents)
        } for field_id, field_contents in contents_by_field.items()
    ]


def __get_response_dict(exercise: Exercise, segel_only: bool) -> Dict[str, Any]:
    test_responses = [resp for resp in __test_responses.values() if resp.segel_only == segel_only]

    current_response_types = \
        (resp.response_type.value for resp in test_responses)
    current_checker_name =\
        (resp.hide_checker_name for resp in test_responses)

    response_type: ResponseType = ResponseType(max(current_response_types))
    hide_checker_name: bool = any(current_checker_name)

    return {
        "contents": __get_contents_array(exercise, segel_only),
        "type": response_type.name,
        "segel_only": segel_only,
        "hide_checker_name": hide_checker_name,
    }


def write_output(exercise: Exercise) -> None:
    data = []

    has_segel_only = any((res.segel_only for res in __test_responses.values()))
    has_hanich_view = [res.segel_only for res in __test_responses.values() if res.segel_only is False] != []
    if has_segel_only:
        data.append(__get_response_dict(exercise, segel_only=True))
    if has_hanich_view:
        data.append(__get_response_dict(exercise, segel_only=False))

    with open('/mnt/autocheck/output.json', 'w', encoding='utf-8') as output_file:
        json.dump(data, output_file)


def __add_error_response():
    framework_error_message = '''One or more of your autochecks failed!
please see autocheck logs for more info...'''

    contents = [ ContentDescriptor(framework_error_message, None) ]

    __test_responses['Hive-Tester-Framework'] = AutocheckResponse(contents,
                                                                  ResponseType.Redo,
                                                                  segel_only=True)


def autocheck(func = None, *, test_title = None):
    if func is None:
        return partial(autocheck, test_title=test_title)

    test_title = test_title or func.__name__

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            response: Optional[AutocheckResponse] = func(*args, **kwargs)
            if response is not None:
                __test_responses[test_title] = response
        except:
            __add_error_response()

    return wrapper
