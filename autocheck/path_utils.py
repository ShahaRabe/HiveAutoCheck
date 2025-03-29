import contextlib
import os
from pathlib import Path
from collections.abc import Generator


@contextlib.contextmanager
def push_dir(new_dir: Path) -> Generator[None, None, None]:
    """
    Starts a scope where the cwd is `new_dir`.
    Once the scope ends the cwd reverts to what it was.
    Can be nested.
    """
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)
