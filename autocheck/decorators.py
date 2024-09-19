from decorator import decorator

from autocheck import InputOutputJson, AutocheckResponse
from conftest import get_exercise

def autocheck(func):
    def wrapper(func, *args, **kwargs):
        response: AutocheckResponse = func(*args, **kwargs)
        InputOutputJson.write_output(get_exercise(), response)
    
    return decorator(wrapper, func)
