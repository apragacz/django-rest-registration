import functools
import types

from django.core.checks import Error


def api_view_serializer_class_getter(serializer_class_getter):

    def _get_serializer_class(self):
        return serializer_class_getter()

    def _get_serializer(self):
        cls = self.get_serializer_class()
        return cls()

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
