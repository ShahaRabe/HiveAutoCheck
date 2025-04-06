import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any

import wrapt
from deprecated import deprecated

from .exercise import Exercise, FieldType
from .output import AutocheckOutput, HiveFieldContentDict, ResponseType
from .settings import settings

logger = logging.getLogger(__name__)


@dataclass
class ContentDescriptor:
    content: str
    field_name: str | None


@dataclass
class AutocheckResponse:
    content_descriptors: list[ContentDescriptor]
    response_type: ResponseType
    segel_only: bool = True
    hide_checker_name: bool = True


__test_responses: dict[str, AutocheckResponse] = {}


def __get_contents_array(
    exercise: Exercise,
    segel_only: bool,  # noqa: FBT001
) -> list[HiveFieldContentDict]:
    contents_by_field: dict[int, list[str]] = {}
    for test, response in __test_responses.items():
        if response.segel_only != segel_only:
            continue

        for desc in response.content_descriptors:
            if desc.field_name is None:
                field_names = [
                    field.name
                    for field in exercise.fields
                    if field.has_value and field.type == FieldType.TEXT
                ]
            else:
                field_names = [desc.field_name]

            for field_name in field_names:
                field_id: int = exercise.get_field_id(field_name)
                if field_id not in contents_by_field:
                    contents_by_field[field_id] = []

                contents_by_field[field_id].append(f"### {test}:\n{desc.content}")

    return [
        {"field": field_id, "content": "\n\n".join(field_contents)}
        for field_id, field_contents in contents_by_field.items()
    ]


def __get_output_json(exercise: Exercise, segel_only: bool) -> AutocheckOutput:  # noqa: FBT001
    test_responses = [
        resp for resp in __test_responses.values() if resp.segel_only == segel_only
    ]

    current_response_types = (resp.response_type for resp in test_responses)
    current_checker_name = (resp.hide_checker_name for resp in test_responses)

    response_type = max(current_response_types)
    hide_checker_name = any(current_checker_name)

    return AutocheckOutput(
        contents=__get_contents_array(exercise, segel_only),
        type=response_type,
        segel_only=segel_only,
        hide_checker_name=hide_checker_name,
    )


def write_output(exercise: Exercise) -> None:
    data: list[dict[str, Any]] = []

    has_segel_only = any(res.segel_only for res in __test_responses.values())
    has_hanich_view = any(not res.segel_only for res in __test_responses.values())
    if has_segel_only:
        data.append(__get_output_json(exercise, segel_only=True).model_dump())
    if has_hanich_view:
        data.append(__get_output_json(exercise, segel_only=False).model_dump())

    with settings.hive_output_json_path.open("w", encoding="utf-8") as output_file:
        json.dump(data, output_file)


def __add_error_response() -> None:
    framework_error_message = ("One or more of your autochecks failed!\n"
                               "Please see autocheck logs for more info...")

    contents = [ContentDescriptor(framework_error_message, None)]

    __test_responses["Hive-Tester-Framework"] = AutocheckResponse(
        contents,
        ResponseType.Redo,
        segel_only=True,
    )


_AutocheckCallable = Callable[..., AutocheckResponse | bool | None]


def autocheck(*, test_title: str | None = None) -> _AutocheckCallable:
    # https://wrapt.readthedocs.io/en/master/decorators.html#decorators-with-arguments
    @wrapt.decorator  # type: ignore
    def wrapper(
        wrapped: _AutocheckCallable,
        _: object | None,
        args: tuple[str, ...],
        kwargs: dict[str, Any],
    ) -> None:
        try:
            response = wrapped(*args, **kwargs)
            if response is not None:
                match response:
                    case bool():
                        logger.debug("A boolean was returned")
                        response = bool_to_response(response)
                    case AutocheckResponse():
                        logger.debug("An AutocheckResponse was returned")
                    case _:
                        raise ValueError(  # noqa: TRY301
                            "An autocheck must return an "
                            "AutocheckResponse or a boolean",
                        )

                __test_responses[test_title or wrapped.__name__] = response

        except Exception:
            logger.exception("An autocheck has raised an exception")
            __add_error_response()

    return wrapper  # type: ignore


def bool_to_response(boolean: bool) -> AutocheckResponse:  # noqa: FBT001
    """Basic transformation of boolean result to a simple AutocheckResponse.

    Not fit for hanich's eyes
    """
    return AutocheckResponse(
        [ContentDescriptor("Success!" if boolean else "Fail!", "Comment")],
        ResponseType.AutoCheck if boolean else ResponseType.Redo,
    )


@deprecated(version="0.2.0", reason="Use `@autocheck()` instead")
def boolean_test(func: Callable[..., bool]) -> Callable[..., AutocheckResponse]:
    """Convert a boolean function to a test that can be fed to @autocheck.

    Uses bool_to_response, so also not fit for hanich's eyes
    """

    @wraps(func)
    def wrapper(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> AutocheckResponse:
        response: bool = func(*args, **kwargs)
        return bool_to_response(response)

    return wrapper
