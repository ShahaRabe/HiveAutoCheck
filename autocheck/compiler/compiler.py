from abc import ABC, abstractmethod
from pathlib import Path

from autocheck.compiler.exceptions import CompilationError
from autocheck.exercise import Exercise


class Compiler(ABC):
    """A compiler for solutions of exercises."""

    @staticmethod
    @abstractmethod
    def compile(
        solution_directory_path: Path,
        exercise_name: str | None,
    ) -> tuple[int, bytes, bytes]:
        """Compiles a solution.

        :returns: Compilation result and output
        """

    @staticmethod
    @abstractmethod
    def find_executable_path(solution_directory_path: Path, exercise_name: str) -> Path:
        pass


def compile_and_get_executable_path(
    cloned_repository: Path,
    exercise: Exercise,
    compiler_type: type[Compiler],
) -> Path:
    result, out, err = compiler_type.compile(cloned_repository, exercise.name)
    if result == 0:
        return compiler_type.find_executable_path(cloned_repository, exercise.name)

    if err:
        raise CompilationError(f"Solution build failed:\n{err.decode()}")
    raise CompilationError(f"Solution build failed:\n{out.decode()}")
