class CompilationException(Exception):
    pass


class CompilationCleaningException(Exception):
    pass


class TimeoutException(Exception):
    pass


class InvalidExitCodeError(Exception):
    exit_code: str

    def __init__(self, exit_code: str):
        super().__init__(f"Could not parse exit code as int: '{exit_code}'")
        self.exit_code = exit_code


class MasmHeaderNotFoundError(Exception):
    stdout: str

    def __init__(self, stdout: str):
        super().__init__(f"Could not find MASM header: \n\n{stdout}")
        self.stdout = stdout


class CompileError(Exception):
    """
    Represents a 'safe' compilation error.
    This error can be displayed to the user.
    """

    stdout: str

    def __init__(self, stdout: str):
        super().__init__(f"=== Compilation failed\n\n{stdout}")
        self.stdout = stdout
