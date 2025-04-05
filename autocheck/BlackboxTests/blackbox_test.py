import contextlib
import logging
import shutil
import subprocess
import sys
import threading
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path

from .blackbox_test_config import BlackboxTestConfig

logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    is_success: bool
    output: str | None = None


@contextlib.contextmanager
def additional_files_context(
    additional_files: dict[Path, Path] | None,
    working_directory: Path,
) -> Generator[None, None, None]:
    files: dict[Path, Path] = additional_files or {}
    for src_file, dst_file in files.items():
        shutil.copy2(src_file, working_directory / dst_file)
    yield
    for dst_file in files.values():
        dst_file.unlink()


class BlackboxTest:
    __DEFAULT_EXECUTABLE_TIMEOUT = 1 * 60

    @staticmethod
    def check_excepted_output(
        test_config: BlackboxTestConfig,
        solution_output: str,
    ) -> TestResult:
        solution_output = solution_output.replace("\r", "")  # ignore CR ("\r")

        # search for all outputs in order
        last_found_output_index = 0
        for expected_output in test_config.expected_output:
            expected_output = expected_output.replace("\r", "")
            found_index = solution_output.find(expected_output, last_found_output_index)

            not_found_index = -1
            if found_index == not_found_index:
                descriptive_error_message = (
                    f"Test case '{test_config.description}'\n"
                    f"Input: {test_config.input}\n"
                    f"The output {expected_output.strip()} is not "
                    f"in your program output\n"
                )

                error_message = (
                    test_config.custom_error_message or descriptive_error_message
                )
                return TestResult(is_success=False, output=error_message)

            last_found_output_index = found_index

        return TestResult(is_success=True)

    def run_executable_with_timeout(
        self,
        program: str,
        timeout_in_seconds: int,
        program_cmdline_args: list[str] | None = None,
        stdin_string: str | None = None,
    ) -> None:
        self.process = None
        self.stdout = None
        self.err = None
        self.reach_timeout = False

        # On Windows, communicate adds LF automatically,
        # but on Linux, we have to and it manually.
        if stdin_string and (sys.platform == "linux" or sys.platform == "linux2"):
            stdin_string += "\n"

        def target() -> None:
            cmdline = [program]
            if program_cmdline_args:
                cmdline += program_cmdline_args

            self.process = subprocess.Popen(
                cmdline,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            self.stdout, self.err = self.process.communicate(stdin_string)

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout_in_seconds)
        assert self.process is not None
        if thread.is_alive():
            self.process.terminate()
            self.process.wait()
            thread.join()
            self.reach_timeout = True

    def run_test(
        self,
        program: str,
        test_configs: list[BlackboxTestConfig],
        working_directory: Path,
        timeout_in_seconds: int = __DEFAULT_EXECUTABLE_TIMEOUT,
    ) -> TestResult:
        logger.info("Entered test_blackbox")

        for test in test_configs:
            logger.info(f"Running {program} with input {test.input}")

            with additional_files_context(
                test.additional_files_mapping,
                working_directory,
            ):
                self.run_executable_with_timeout(
                    program,
                    timeout_in_seconds=timeout_in_seconds,
                    program_cmdline_args=test.cmdline_args,
                    stdin_string=" ".join(test.input),
                )

            if self.reach_timeout:
                return TestResult(
                    is_success=False,
                    output=f"Running timed out after {timeout_in_seconds} seconds.",
                )

            assert self.process is not None
            if self.process.returncode != 0:
                program_input_text: str = (
                    f"with the input {test.input}" if test.input else "with no input"
                )
                return TestResult(
                    is_success=False,
                    output=f"Running the program {program_input_text} "
                           f"failed with the result code {self.process.returncode}.",
                )

            test_result = BlackboxTest.check_excepted_output(
                test,
                self.stdout or "",
            )
            if not test_result.is_success:
                return test_result

        return TestResult(is_success=True)
