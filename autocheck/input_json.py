from dataclasses import dataclass
from typing import List, Dict, Any, Literal, Optional


@dataclass
class InputJSON:
    """
    This class represents the structure of the JSON file
    written by Hive to `/mnt/autocheck/input.json` inside the
    autocheck docker container.

    The exact structure is derived
    from:    `autocheck/autocheck/check/checker.py`
    at:      `__upload_check_request`
    in the Hive sources.
    """

    file: Optional[str]
    file_name: str
    contents: List[Dict[str, Any]]
    form_fields: List[Dict[str, Any]]
    assignment_id: int
    description: Optional[str]

    """
    The type hints are derived
    from:    `core/core/management/models.py`
    at:      `class Gender[...]`
    in the Hive sources.
    """
    user_gender: Literal["Male", "Female", "NonBinary"]

    def get_field_content(self, field_name: str) -> Optional[str]:
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
