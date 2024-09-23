from typing import Optional
from functools import wraps, partial

from autocheck import InputOutputJson, AutocheckResponse

def autocheck(func = None, *, test_title = None):
    if func is None:
        return partial(autocheck, test_title=test_title)

    test_title = test_title or func.__name__

    @wraps(func)
    def wrapper(*args, **kwargs):
        response: Optional[AutocheckResponse] = func(*args, **kwargs)

        if response is not None:
            InputOutputJson.add_response(test_title, response)

    return wrapper
