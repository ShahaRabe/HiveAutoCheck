import logging
import os
import subprocess
from pathlib import Path
from typing import Optional

from .compiler import Compiler
from .exceptions import CompilationException
from ..path_utils import push_dir

class MakeCompiler(Compiler):
    """
    Compiler for exercises compiled with make.
    Currently support gcc, g++ and clang.
    """
    _COMPILATION_FAILURE_RETURN_VALUE = 2
    _MAKEFILE_POSSIBLE_NAMES = ["makefile", "Makefile"]
    _OUTPUT_DIR_NAME = 'bin'

    @staticmethod
    def compile(solution_directory_path: Path, exercise_name: Optional[str] = None):
        logging.info("compile with MakeCompiler")

        MakeCompiler.validate_makefile_exists(solution_directory_path)

        with push_dir(solution_directory_path):
            proc = subprocess.Popen(
                [f'make'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )

        out, err = proc.communicate()

        if MakeCompiler._COMPILATION_FAILURE_RETURN_VALUE == proc.returncode:
            raise CompilationException(
                f"Running make failed with return code {proc.returncode}.\n\n"
                f"Compilation stdout:\n"
                f"{out}\n\n"
                f"Compilation stderr:\n{err}"
            )

        return proc.returncode, out, err

    @staticmethod
    def find_executable_path(solution_directory_path: Path, exercise_name: str) -> Path:
        exercise_name: str = "".join(exercise_name.lower().split())
        bin_dir_path: Path = solution_directory_path / MakeCompiler._OUTPUT_DIR_NAME

        if not bin_dir_path.exists():
            raise CompilationException("The executables directory doesn’t exist within the solution")

        files_in_bin_dir = os.listdir(bin_dir_path)
        if len(files_in_bin_dir) == 1:
            return bin_dir_path / files_in_bin_dir[0]

        for file_name in files_in_bin_dir:
            if file_name.lower() == exercise_name:
                return bin_dir_path / file_name

        raise CompilationException("The executables directory should contain a file named like the exercise in one word, or exactly 1 file")

    @staticmethod
    def validate_makefile_exists(solution_directory_path: Path):
        if not any((solution_directory_path / makefile).exists() for makefile in MakeCompiler._MAKEFILE_POSSIBLE_NAMES):
            raise CompilationException("No makefile found.")
