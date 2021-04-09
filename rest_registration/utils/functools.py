from functools import WRAPPER_ASSIGNMENTS, WRAPPER_UPDATES
from typing import Any, Callable, Iterable, TypeVar

_T = TypeVar('_T')


# Copied from stdlib functools module
def update_wrapper(
        wrapper: Any,
        wrapped: Callable[..., _T],
        assigned: Iterable[str] = WRAPPER_ASSIGNMENTS,
        updated: Iterable[str] = WRAPPER_UPDATES,
        set_wrapped: bool = True):
    for attr in assigned:
        try:
            value = getattr(wrapped, attr)
        except AttributeError:
            pass
        else:
            setattr(wrapper, attr, value)
    for attr in updated:
        getattr(wrapper, attr).update(getattr(wrapped, attr, {}))
    if set_wrapped:
        # Issue #17482: set __wrapped__ last so we don't inadvertently copy it
        # from the wrapped function when updating __dict__
        wrapper.__wrapped__ = wrapped
    # Return the wrapper so this can be used as a decorator via partial()
    return wrapper
