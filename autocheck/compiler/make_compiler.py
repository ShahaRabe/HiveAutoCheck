import logging
import pathlib
import subprocess
import typing
from pathlib import Path

from autocheck.compiler.compiler import Compiler
from autocheck.compiler.exceptions import CompilationError
from autocheck.path_utils import push_dir

logger = logging.getLogger(__name__)

class MakeCompiler(Compiler):
    """Compiler for exercises compiled with make.

    Currently, supports gcc, g++ and clang.
    """

    _COMPILATION_FAILURE_RETURN_VALUE = 2
    _MAKEFILE_POSSIBLE_NAMES: typing.ClassVar = ["makefile", "Makefile"]
    OUTPUT_DIR_NAME = "bin"

    @staticmethod
    def compile(
        solution_directory_path: Path,
        _: str | None = None,
    ) -> tuple[int, bytes, bytes]:
        logger.info("compile with MakeCompiler")

        MakeCompiler.validate_makefile_exists(solution_directory_path)

        with push_dir(solution_directory_path):
            proc = subprocess.Popen(
                ["make"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )

        out, err = proc.communicate()

        if proc.returncode == MakeCompiler._COMPILATION_FAILURE_RETURN_VALUE:
            raise CompilationError(
                (
                    f"Running make failed with return code {proc.returncode}.\n\n"
                    f"Compilation stdout:\n"
                    f"{out.decode()}\n\n"
                    f"Compilation stderr:\n{err.decode()}"
                ),
            )

        return proc.returncode, out, err

    @staticmethod
    def find_executable_path(solution_directory_path: Path, exercise_name: str) -> Path:
        exercise_name = "".join(exercise_name.lower().split())
        bin_dir_path: Path = solution_directory_path / MakeCompiler.OUTPUT_DIR_NAME

        if not bin_dir_path.exists():
            raise CompilationError(
                "The executables directory doesn't exist within the solution",
            )

        files_in_bin_dir = list(pathlib.Path(bin_dir_path).iterdir())
        if len(files_in_bin_dir) == 1:
            return bin_dir_path / files_in_bin_dir[0]

        for file_name in files_in_bin_dir:
            if file_name.lower() == exercise_name:
                return bin_dir_path / file_name

        raise CompilationError(
            "The executables directory should contain a file named "
            "like the exercise in one word, or exactly 1 file",
        )

    @staticmethod
    def validate_makefile_exists(solution_directory_path: Path) -> None:
        if not any(
            (solution_directory_path / makefile).exists()
            for makefile in MakeCompiler._MAKEFILE_POSSIBLE_NAMES
        ):
            raise CompilationError("No makefile found.")
