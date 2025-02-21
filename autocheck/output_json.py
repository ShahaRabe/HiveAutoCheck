from dataclasses import dataclass, field
from typing import List, Literal


@dataclass(frozen=True)
class OutputJSON:
    type: Literal["AutoCheck", "Done", "Redo"]
    segel_only: bool = True
    hide_checker_name: bool = True
    contents: List = field(default_factory=list)
