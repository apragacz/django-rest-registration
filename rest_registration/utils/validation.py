import functools
from collections import OrderedDict
from collections.abc import Mapping
from typing import Any, Callable, Dict, Iterable, List

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext as _
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework.settings import api_settings

from rest_registration.utils.users import build_initial_user

Validator = Callable[[Any], None]


def wrap_validation_error_with_field(field_name: str):

    def decorator(func: Validator):

        @functools.wraps(func)
        def wrapper(value: Any) -> None:
            try:
                func(value)
            except ValidationError as exc:
                raise ValidationError({field_name: exc.detail})

        return wrapper

    return decorator


@wrap_validation_error_with_field('password_confirm')
def validate_user_password_confirm(user_data: Dict[str, Any]) -> None:
    if user_data['password'] != user_data['password_confirm']:
        raise ValidationError(ErrorDetail(
            _("Passwords don't match"),
            code='passwords-do-not-match'),
        )


@wrap_validation_error_with_field('password')
def validate_user_password(user_data: Dict[str, Any]) -> None:
    password = user_data['password']
    user = build_initial_user(user_data)
    try:
        validate_password(password, user=user)
    except DjangoValidationError as exc:
        # TODO: Issue #109 - remove type: ignore
        raise ValidationError(list(exc.messages))  # type: ignore


def run_validators(validators: Iterable[Validator], value: Any) -> None:
    fields_errors = OrderedDict()  # type: Dict[str, Any]
    non_field_errors = []  # type: List[Any]
    for validator in validators:
        try:
            validator(value)
        except ValidationError as exc:
            if isinstance(exc.detail, Mapping):
                for field_name, field_errors in exc.detail.items():
                    fields_errors.setdefault(field_name, []).extend(
                        field_errors)
            elif isinstance(exc.detail, list):
                non_field_errors.extend(exc.detail)

    if fields_errors:
        errors = {}
        errors.update(fields_errors)
        errors.setdefault(
            api_settings.NON_FIELD_ERRORS_KEY, []).extend(non_field_errors)
        raise ValidationError(errors)
    if non_field_errors:
        # TODO: Issue #109 - remove type: ignore
        raise ValidationError(non_field_errors)  # type: ignore
