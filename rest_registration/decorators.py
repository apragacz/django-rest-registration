import functools
import types
from typing import Callable, List, Union

from django.core import checks

from rest_registration.enums import ErrorCode, WarningCode
from rest_registration.utils.functools import update_wrapper

WRAPPER_ASSIGNMENTS_WITHOUT_ANNOTATIONS = tuple(
    a for a in functools.WRAPPER_ASSIGNMENTS if a != '__annotations__')


def api_view_serializer_class_getter(serializer_class_getter):

    def _get_serializer_class(self):
        return serializer_class_getter()

    def _get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        return serializer_class(*args, **kwargs)

    def decorator(func):
        if not hasattr(func, 'cls'):
            raise Exception(
                '@api_view_serializer_class_getter can only decorate'
                ' @api_view decorated functions')
        apiview_cls = func.cls
        apiview_cls.get_serializer_class = types.MethodType(
            _get_serializer_class,
            apiview_cls)
        if not hasattr(apiview_cls, 'get_serializer'):
            # In case get_serializer() method is missing.
            apiview_cls.get_serializer = types.MethodType(
                _get_serializer,
                apiview_cls)
        return func
    return decorator


def api_view_serializer_class(serializer_class):
    return api_view_serializer_class_getter(lambda: serializer_class)


def simple_check(
        error_message: str, error_code: Union[ErrorCode, WarningCode],
        obj=None):
    warning = isinstance(error_code, WarningCode)
    message_cls = checks.Warning if warning else checks.Error

    def decorator(predicate: Callable[[], bool]):

        def check_fun(
                app_configs, **kwargs) -> List[checks.CheckMessage]:
            from rest_registration.apps import RestRegistrationConfig  # noqa: E501 pylint: disable=import-outside-toplevel, cyclic-import

            messages = []
            if not predicate():
                err_id = '{RestRegistrationConfig.name}.{error_code}'.format(
                    RestRegistrationConfig=RestRegistrationConfig,
                    error_code=error_code,
                )
                messages.append(
                    message_cls(
                        error_message,
                        obj=obj,
                        hint=None,
                        id=err_id,
                    )
                )
            return messages

        update_wrapper(
            check_fun, predicate,
            assigned=WRAPPER_ASSIGNMENTS_WITHOUT_ANNOTATIONS,
            set_wrapped=False)

        return check_fun

    return decorator
