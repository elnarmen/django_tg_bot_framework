from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Generator


@contextmanager
def set_contextvar(contextvar: ContextVar[Any], value: Any) -> Generator[None, None, None]:
    var_token = contextvar.set(value)
    try:
        yield
    finally:
        contextvar.reset(var_token)
