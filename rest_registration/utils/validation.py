import functools
from collections import OrderedDict
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, List

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext as _
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework.settings import api_settings

from rest_registration.utils.users import (
    build_initial_user,
    get_user_by_verification_id
)

if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser

Validator = Callable[[Any], None]


def wrap_validation_error_with_field(
        field_name: str) -> Callable[[Validator], Validator]:

    def decorator(func: Validator) -> Validator:

        @functools.wraps(func)
        def wrapper(value: Any) -> None:
            try:
                func(value)
            except ValidationError as exc:
                raise ValidationError({field_name: exc.detail}) from None

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
    return _validate_user_password(password, user)


@wrap_validation_error_with_field('password')
def validate_password_with_user_id(user_data: Dict[str, Any]) -> None:
    password = user_data['password']
    user_id = user_data['user_id']
    user = get_user_by_verification_id(user_id, require_verified=False)
    return _validate_user_password(password, user)


def _validate_user_password(password: str, user: 'AbstractBaseUser') -> None:
    try:
        validate_password(password, user=user)
    except DjangoValidationError as exc:
        raise transform_django_validation_error(exc) from None


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
        raise ValidationError(non_field_errors)


def transform_django_validation_error(
    exc: DjangoValidationError
) -> ValidationError:
    if hasattr(exc, 'error_dict'):
        return ValidationError(_extract_error_detail_dict(exc.error_dict))
    return ValidationError(_extract_error_detail_list(exc.error_list))


def _extract_error_detail_dict(
    exc_data: Dict[str, List[DjangoValidationError]]
) -> Dict[str, List[ErrorDetail]]:
    err_detail_dict = {}
    for key, exc_list in exc_data.items():
        err_detail_dict[key] = _extract_error_detail_list(exc_list)
    return err_detail_dict


def _extract_error_detail_list(
    exc_data: List[DjangoValidationError]
) -> List[ErrorDetail]:
    err_details = []
    for sub_exc in exc_data:
        for err_detail in _shallow_extract_error_details_from_exc(sub_exc):
            err_details.append(err_detail)
    return err_details


def _shallow_extract_error_details_from_exc(
    exc: DjangoValidationError
) -> List[ErrorDetail]:
    if hasattr(exc, 'message') and hasattr(exc, 'code'):
        message = exc.message
        if exc.params:
            message %= exc.params
        return [ErrorDetail(message, code=exc.code)]
    return [ErrorDetail(msg) for msg in exc.messages]
