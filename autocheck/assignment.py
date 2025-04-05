from pydantic import BaseModel


class Assignment(BaseModel):
    id: int
    description: str
    exercise: int
