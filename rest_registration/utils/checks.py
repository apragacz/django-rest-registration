import functools
from typing import Any, Callable, Iterable, List, Type, Union

from django.apps import AppConfig
from django.core import checks

from rest_registration.utils.functools import update_wrapper

WRAPPER_ASSIGNMENTS_WITHOUT_ANNOTATIONS = tuple(
    a for a in functools.WRAPPER_ASSIGNMENTS if a != '__annotations__')

CheckMessage = Union[checks.Error, checks.Warning]


class CheckCode:

    def get_full_code_id(self) -> str:
        app_name = self.get_app_name()
        code_id = self.get_code_id()
        return '{app_name}.{code_id}'.format(app_name=app_name, code_id=code_id)

    def get_app_name(self) -> str:
        raise NotImplementedError()

    def get_code_id(self) -> str:
        raise NotImplementedError()

    def get_check_message_class(self) -> Type[CheckMessage]:
        raise NotImplementedError()


def predicate_check(
        error_message: str, error_code: CheckCode,
        obj: Any = None
) -> Callable[[Callable[[], bool]], Callable[..., List[checks.CheckMessage]]]:
    message_cls = error_code.get_check_message_class()

    def decorator(
            predicate: Callable[[], bool]
    ) -> Callable[..., List[checks.CheckMessage]]:

        def check_fun(
                app_configs: Iterable[AppConfig], **kwargs,
        ) -> List[checks.CheckMessage]:
            if predicate():
                return []

            return [
                message_cls(
                    error_message,
                    obj=obj,
                    hint=None,
                    id=error_code.get_full_code_id(),
                )
            ]

        update_wrapper(
            check_fun, predicate,
            assigned=WRAPPER_ASSIGNMENTS_WITHOUT_ANNOTATIONS,
            set_wrapped=False)

        return check_fun

    return decorator


def no_exception_check(
        error_message: str, error_code: CheckCode,
        obj: Any = None
) -> Callable[[Callable[[], None]], Callable[..., List[checks.CheckMessage]]]:
    message_cls = error_code.get_check_message_class()

    def decorator(
            fun: Callable[[], None]
    ) -> Callable[..., List[checks.CheckMessage]]:

        def check_fun(
                app_configs: Iterable[AppConfig], **kwargs,
        ) -> List[checks.CheckMessage]:
            try:
                fun()
            except Exception as exc:  # pylint: disable=broad-except
                exc_str = str(exc)
                msg = '{error_message}: {exc_str}'.format(
                    error_message=error_message, exc_str=exc_str)
                return [
                    message_cls(
                        msg,
                        obj=obj,
                        hint=None,
                        id=error_code.get_full_code_id(),
                    )
                ]
            else:
                return []

        update_wrapper(
            check_fun, fun,
            assigned=WRAPPER_ASSIGNMENTS_WITHOUT_ANNOTATIONS,
            set_wrapped=False)

        return check_fun

    return decorator
