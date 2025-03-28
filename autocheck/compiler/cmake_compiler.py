import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple

from .make_compiler import MakeCompiler
from .exceptions import CompilationException
from ..path_utils import push_dir


class CMakeCompiler(MakeCompiler):
    """
    Compiler for exercises compiled with cmake.
    """
    CMAKE_COMMAND = ["/usr/bin/cmake", "../"]
    MAKE_COMMAND = ["make"]
    COMPILATION_SUCCESS_RETURN_VALUE = 0
    CMAKE_BUILD_DIR = "build"

    @staticmethod
    def compile(solution_directory_path: Path, exercise_name: Optional[str] = None) -> Tuple[int, bytes, bytes]:
        build_dir = solution_directory_path / CMakeCompiler.CMAKE_BUILD_DIR
        build_dir.mkdir(parents=True, exist_ok=True)

        with push_dir(build_dir):
            proc = subprocess.Popen(
                CMakeCompiler.CMAKE_COMMAND,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )

        out, err = proc.communicate()
        if proc.returncode != CMakeCompiler.COMPILATION_SUCCESS_RETURN_VALUE:
            raise CompilationException(
                f"Running cmake failed with return code {proc.returncode}.\n\n"
                f"Compilation stdout:\n"
                f"{out.decode()}\n\n"
                f"Compilation stderr:\n{err.decode()}"
            )

        return MakeCompiler.compile(build_dir, exercise_name)

    @staticmethod
    def find_executable_path(solution_directory_path: Path, exercise_name: str) -> Path:
        exercise_name = "".join(exercise_name.lower().split())
        build_dir: Path = solution_directory_path / CMakeCompiler.CMAKE_BUILD_DIR
        make_compiler_build_dir = solution_directory_path / MakeCompiler._OUTPUT_DIR_NAME

        if not build_dir.exists():
            raise CompilationException("The executables directory doesn’t exist within the solution")

        if build_dir != make_compiler_build_dir:
            os.link(build_dir, make_compiler_build_dir)

        return MakeCompiler.find_executable_path(solution_directory_path, exercise_name)
