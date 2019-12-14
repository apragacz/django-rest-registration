from typing import Any, Callable, Union

LazyBool = Callable[[], bool]


def identity(value: Any) -> Any:
    return value


def implies(premise: bool, conclusion: Union[bool, LazyBool]) -> bool:
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
    _conclusion = conclusion() if callable(conclusion) else conclusion
    return _conclusion
