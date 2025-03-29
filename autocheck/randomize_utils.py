import random
import string


def random_string(min_len: int = 0, max_len: int = 100) -> str:
    length = random.randint(min_len, max_len)
    res = ""
    safe_printable = string.ascii_letters + string.digits
    for i in range(length):
        res += random.choice(safe_printable)

    return res


def random_bytearray(min_len: int = 0, max_len: int = 100) -> bytes:
    length = random.randint(min_len, max_len)
    return random.randbytes(length)
