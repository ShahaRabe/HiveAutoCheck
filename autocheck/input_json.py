from typing import Any, Literal

from pydantic import BaseModel


class InputJSON(BaseModel):  # TODO: Consider renaming to `AutocheckInput`
    """The input file mounted by Hive.

    The exact structure is derived
    from:    `autocheck/autocheck/check/checker.py`
    at:      `__upload_check_request`
    in the Hive sources.
    """

    file: str | None
    file_name: str
    contents: list[dict[str, Any]]
    form_fields: list[dict[str, Any]]
    assignment_id: int
    description: str | None

    """
    The type hints are derived
    from:    `core/core/management/models.py`
    at:      `class Gender[...]`
    in the Hive sources.
    """
    user_gender: Literal["Male", "Female", "NonBinary"]

    def get_field_content(self, field_name: str) -> str | None:
        entries = list(
            filter(lambda entry: entry["name"] == field_name, self.form_fields)
        )
        if len(entries) == 0:
            return None

        entry_id: int = entries[0]["id"]
        content: str = next(
            filter(lambda entry: entry["field"] == entry_id, self.contents)
        )["content"]
        return content
