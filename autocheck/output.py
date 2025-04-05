from enum import StrEnum

from pydantic import BaseModel

HiveFieldContentDict = dict[str, int | str]


class ResponseType(StrEnum):
    AutoCheck = "AutoCheck"
    Done = "Done"
    Redo = "Redo"

    def __lt__(self, other: "ResponseType") -> bool:
        ordering = {
            ResponseType.AutoCheck: 0,
            ResponseType.Done: 1,
            ResponseType.Redo: 2,
        }
        return ordering[self] < ordering[other]


class AutocheckOutput(BaseModel):
    type: ResponseType
    segel_only: bool = True
    hide_checker_name: bool = True
    contents: list[HiveFieldContentDict] = []
