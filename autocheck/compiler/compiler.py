from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Type, Tuple

from ..exercise import Exercise
from .exceptions import CompilationException


class Compiler(ABC):
    """
    A compiler for solutions of exercises
    """

    @staticmethod
    @abstractmethod
    def compile(solution_directory_path: Path, exercise_name: Optional[str]) -> Tuple[int, bytes, bytes]:
        """
        Compiles a solution
        :param: solution_directory_path: The path to the solution
        :param: exercise_name: Name of the exercise
        :returns: Compilation result and output
        """

    pass

    @staticmethod
    @abstractmethod
    def find_executable_path(solution_directory_path: Path, exercise_name: str) -> Path:
        pass


def compile_and_get_executable_path(cloned_repository: Path, exercise: Exercise, compiler_type: Type[Compiler]) -> Path:
    result, out, err = compiler_type.compile(cloned_repository, exercise.name)
    if result == 0:
        return compiler_type.find_executable_path(cloned_repository, exercise.name)

    if err:
        raise CompilationException(f"Solution build failed:\n{err.decode()}")
    raise CompilationException(f"Solution build failed:\n{out.decode()}")
