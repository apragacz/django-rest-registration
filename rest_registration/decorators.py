import functools
import types

from django.core.checks import Error


def serializer_class_getter(class_getter):

    def _get_serializer_class(self):
        return class_getter()

    def decorator(func):
        if not hasattr(func, 'cls'):
            raise Exception('@serializer_class_getter can only decorate'
                            ' @api_view decorated functions')
        apiview_cls = func.cls
        apiview_cls.get_serializer_class = types.MethodType(
            _get_serializer_class,
            apiview_cls)
        return func
    return decorator


def simple_check(error_message, error_code, obj=None):

    def decorator(predicate):

        @functools.wraps(predicate)
        def check_fun(app_configs, **kwargs):
            from rest_registration.apps import RestRegistrationConfig

            errors = []
            if not predicate():
                err_id = '{RestRegistrationConfig.name}.{error_code}'.format(
                    RestRegistrationConfig=RestRegistrationConfig,
                    error_code=error_code,
                )
                errors.append(
                    Error(
                        error_message,
                        obj=obj,
                        hint=None,
                        id=err_id,
                    )
                )
            return errors

        return check_fun

    return decorator
