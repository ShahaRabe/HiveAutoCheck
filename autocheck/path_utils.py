import contextlib
import os
from collections.abc import Generator
from pathlib import Path


@contextlib.contextmanager
def push_dir(new_dir: Path) -> Generator[None, None, None]:
    """Start a scope where the cwd is `new_dir`.

    Once the scope ends the cwd reverts to what it was.
    Can be nested.
    """
    previous_dir = Path.cwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)
