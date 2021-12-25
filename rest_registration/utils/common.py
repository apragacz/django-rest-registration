from enum import Enum
from typing import Callable, Iterable, Optional, Set, TypeVar, Union

_T = TypeVar('_T')
LazyBool = Callable[[], bool]
MaybeLazyBool = Union[bool, LazyBool]


class DefaultValues(Enum):
    RAISE_EXCEPTION = 'raise-exception'


RAISE_EXCEPTION = DefaultValues.RAISE_EXCEPTION


def identity(value: _T) -> _T:
    """
    >>> identity(None)
    >>> identity(1)
    1
    """
    return value


def materialize_bool(value: MaybeLazyBool) -> bool:
    """
    >>> materialize_bool(True)
    True
    >>> materialize_bool(False)
    False
    >>> materialize_bool(lambda: True)
    True
    >>> materialize_bool(lambda: False)
    False
    """
    return value() if callable(value) else value


def implies(premise: bool, conclusion: MaybeLazyBool) -> bool:
    """
    Calculate material implication for given premise and conclusion.
    The conclusion may be lazy evaluated if it is of LazyBool type.
    >>> implies(True, True)
    True
    >>> implies(True, False)
    False
    >>> implies(False, True)
    True
    >>> implies(False, False)
    True
    >>> implies(True, lambda: True)
    True
    >>> implies(True, lambda: False)
    False
    >>> implies(False, lambda: True)
    True
    >>> implies(False, lambda: False)
    True
    """
    if not premise:
        return True
    return materialize_bool(conclusion)


def set_or_none(iterable: Optional[Iterable[_T]]) -> Optional[Set[_T]]:
    """
    >>> set_or_none(None)
    >>> set_or_none([1,1,2]) == {1,2}
    True
    """
    if iterable is None:
        return None
    return set(iterable)
