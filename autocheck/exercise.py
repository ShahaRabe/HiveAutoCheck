from dataclasses import dataclass
from typing import List
from enum import Enum


class FieldType(Enum):
    Text = "text"
    Number = "number"


@dataclass
class Field:
    """Class representing a field in an exercise"""

    id: int
    name: str
    has_value: bool
    type: FieldType


@dataclass
class Exercise:
    """Class representing an exercise."""

    id: int
    name: str
    module_name: str
    subject_letter: str
    subject_name: str
    fields: List[Field]

    def get_field_id(self, field_name: str) -> int:
        fields_with_name: List[Field] = list(
            filter(lambda field: field.name == field_name, self.fields)
        )

        assert fields_with_name, f"No field named {field_name}"
        return fields_with_name[0].id
