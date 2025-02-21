import logging
import shutil
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict

from .blackbox_test_config import BlackboxTestConfig


@dataclass
class TestResult:
    is_success: bool
    output: Optional[str] = None


class AdditionFilesContext:
    def __init__(self, additional_files: Dict[Path, Path], working_directory: Path):
        self._additional_files: Dict[Path, Path] = additional_files
        self._working_directory: Path = working_directory

    def __enter__(self):
        for src_file, dst_file in self._additional_files.items():
            shutil.copy2(src_file, self._working_directory / dst_file)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for dst_file in self._additional_files.values():
            dst_file.unlink()


class BlackboxTest:
    __DEFAULT_EXECUTABLE_TIMEOUT = 1 * 60
    
    @staticmethod
    def check_excepted_output(test_config: BlackboxTestConfig, solution_output: str) -> TestResult:
        solution_output = solution_output.replace("\r", "") # ignore CR ("\r")

        #search for all outputs in order
        last_found_output_index = 0
        for expected_output in test_config.expected_output:
            expected_output = expected_output.replace("\r", "")
            found_index = solution_output.find(expected_output, last_found_output_index)

            NOT_FOUND_INDEX: int = -1
            if found_index == NOT_FOUND_INDEX:
                descriptive_error_message: str = (f"Test case '{test_config.description}'\n"
                                                  f"Input: {test_config.input}\n"
                                                  f"The output {expected_output.strip()} is not in your program output\n")

                error_message: str = test_config.custom_error_message or descriptive_error_message
                return TestResult(is_success=False, output=error_message)

            last_found_output_index = found_index

        return TestResult(is_success=True)

    def run_executable_with_timeout(self,
                                    program: str,
                                    timeout_in_seconds: int,
                                    program_cmdline_args: Optional[List[str]] = None,
                                    stdin_string: Optional[str] = None):
        self.process = None
        self.stdout = None
        self.err = None
        self.reach_timeout = False
        
        #On Windows, communicate adds LF outomatically. But on Linux, we have to and it manually.
        if stdin_string and (sys.platform == "linux" or sys.platform == "linux2"):
            stdin_string += "\n"
        
        def target():
            cmdline = [program]
            if program_cmdline_args:
                cmdline += program_cmdline_args
            
            self.process = subprocess.Popen(cmdline,
                                            stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            universal_newlines=True)
            self.stdout, self.err = self.process.communicate(stdin_string)

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout_in_seconds)
        if thread.is_alive():
            self.process.terminate()
            self.process.wait()
            thread.join()
            self.reach_timeout = True

    def run_test(self,
                 program: str,
                 test_configs: List[BlackboxTestConfig],
                 working_directory: Path,
                 timeout_in_seconds=__DEFAULT_EXECUTABLE_TIMEOUT) -> TestResult:
        logging.info("Entered test_blackbox")

        for test in test_configs:
            logging.info(f"Running {program} with input {test.input}")

            with AdditionFilesContext(test.additional_files_mapping, working_directory):
                self.run_executable_with_timeout(program,
                                                 timeout_in_seconds=timeout_in_seconds,
                                                 program_cmdline_args=test.cmdline_args,
                                                 stdin_string=' '.join(test.input))            

            if self.reach_timeout:
                return TestResult(is_success=False, output=f"Running timed out after {timeout_in_seconds} seconds.")
            
            if self.process.returncode != 0:
                program_input_text: str = f"with the input {test.input}" if test.input else "with no input"
                return TestResult(is_success=False,
                                  output=f"Running the program {program_input_text} failed with the result code {self.process.returncode}.")

            test_result: TestResult = BlackboxTest.check_excepted_output(test, self.stdout)
            if not test_result.is_success:
                return test_result
            
        return TestResult(is_success=True)
