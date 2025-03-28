from dataclasses import dataclass, field
from enum import StrEnum
from typing import List, Dict, Any

HiveFieldContentDict = Dict[str, int | str]


class ResponseType(StrEnum):
    AutoCheck = "AutoCheck"
    Done = "Done"
    Redo = "Redo"

    def __lt__(self, other: Any) -> bool:
        ordering = {
            ResponseType.AutoCheck: 0,
            ResponseType.Done: 1,
            ResponseType.Redo: 2,
        }
        return ordering[self] < ordering[other]


@dataclass(frozen=True)
class OutputJSON:
    type: ResponseType
    segel_only: bool = True
    hide_checker_name: bool = True
    contents: List[HiveFieldContentDict] = field(default_factory=list)
