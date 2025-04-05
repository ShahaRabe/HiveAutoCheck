from pydantic import BaseModel


class ExerciseTestMetadata(BaseModel):
    tests: list[str]

    hanich_repository_branch_name: str | None = None
