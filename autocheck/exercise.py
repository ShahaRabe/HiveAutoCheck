from enum import StrEnum, auto
from typing import Annotated

from pydantic import AliasChoices, BaseModel, Field


class FieldType(StrEnum):
    TEXT = auto()
    NUMBER = auto()


class ExerciseField(BaseModel):
    id: int
    name: str
    has_value: bool
    type: FieldType


class GitLabOnCreationData(BaseModel):
    base_branch_name: Annotated[
        str,
        Field(validation_alias=AliasChoices("baseBranchName", "base_branch_name")),
    ]
    work_branch_name: Annotated[
        str,
        Field(validation_alias=AliasChoices("workBranchName", "work_branch_name")),
    ]


class OnCreationData(BaseModel):
    gitlab: GitLabOnCreationData | None = None


class Exercise(BaseModel):
    id: int
    name: str
    module_name: Annotated[str, Field(validation_alias="parent_module_name")]
    subject_letter: Annotated[str, Field(validation_alias="parent_subject_symbol")]
    subject_name: Annotated[str, Field(validation_alias="parent_subject_name")]
    fields: list[ExerciseField]
    on_creation_data: OnCreationData

    def get_field_id(self, field_name: str) -> int:
        fields_with_name = list(
            filter(lambda field: field.name == field_name, self.fields),
        )

        if not fields_with_name:
            raise ValueError(f"No field named {field_name}")

        return fields_with_name[0].id
