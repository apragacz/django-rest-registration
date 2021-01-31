from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Tuple, Union

from django.contrib import auth
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404 as _get_object_or_404

from rest_registration.exceptions import UserNotFound
from rest_registration.settings import registration_settings
from rest_registration.utils.common import set_or_none

_RAISE_EXCEPTION = object()

if TYPE_CHECKING:
    from typing import Optional
    from django.contrib.auth.base_user import AbstractBaseUser
    from django.db.models import Field, ForeignObjectRel

    UserField = Union['Field', 'ForeignObjectRel']


def get_user_by_login_or_none(login, require_verified=False):
    user = None
    for login_field_name in get_user_login_field_names():
        user = get_user_by_lookup_dict(
            {login_field_name: login},
            default=None, require_verified=require_verified)
        if user:
            break

    return user


def authenticate_by_login_data(
        data: Dict[str, Any], **kwargs) -> 'AbstractBaseUser':
    serializer = kwargs.get('serializer')
    if serializer:
        # TODO: Issue #114 - remove code supporting deprecated behavior
        get_authenticated_user = getattr(
            serializer, 'get_authenticated_user', None)
        if callable(get_authenticated_user):
            user = get_authenticated_user()
            if not user:
                raise UserNotFound()
            return user

    login_field_names = get_user_login_field_names()
    password = data.get('password')
    login = data.get('login')
    if password is None:
        raise UserNotFound()
    auth_tests = []  # type: List[Dict[str, Any]]
    if login is not None:
        auth_tests.extend({
            field_name: login,
            'password': password,
        } for field_name in login_field_names)

    for field_name in login_field_names:
        field_value = data.get(field_name)
        if field_value is None:
            continue
        auth_tests.append({
            field_name: field_value,
            'password': password,
        })

    for auth_kwargs in auth_tests:
        user = auth.authenticate(**auth_kwargs)
        if user:
            return user

    raise UserNotFound()


def get_user_login_field_names():
    user_class = get_user_model()
    return get_user_setting('LOGIN_FIELDS') or [user_class.USERNAME_FIELD]


def get_user_verification_id(user):
    verification_id_field = get_user_setting('VERIFICATION_ID_FIELD')
    return getattr(user, verification_id_field)


def get_user_by_verification_id(
        user_verification_id, default=_RAISE_EXCEPTION, require_verified=True):
    verification_id_field = get_user_setting('VERIFICATION_ID_FIELD')
    return get_user_by_lookup_dict({
        verification_id_field: user_verification_id},
        default=default,
        require_verified=require_verified)


def find_user_by_by_send_reset_password_link_data(
        data: Dict[str, Any], **kwargs) -> 'AbstractBaseUser':
    """
    Return user if matching given criteria (login fields / e-mail).
    Return ``None`` otherwise.
    """
    serializer = kwargs.get('serializer')
    if serializer:
        # TODO: Issue #114 - remove code supporting deprecated behavior
        get_user_or_none = getattr(serializer, 'get_user_or_none', None)
        if callable(get_user_or_none):
            user = get_user_or_none()
            if not user:
                raise UserNotFound()
            return user
    login_field_names = get_user_login_field_names()
    finder_tests = [('login', login_field_names)]
    finder_tests.extend((f, [f]) for f in login_field_names)

    for field_name, db_field_names in finder_tests:
        value = data.get(field_name)
        if value is None:
            continue
        for db_fn in db_field_names:
            user = get_user_by_lookup_dict(
                {db_fn: value}, default=None, require_verified=False)
            if user is not None:
                return user

    raise UserNotFound()


def user_with_email_exists(email):
    user_class = get_user_model()
    email_field_name = get_user_email_field_name()
    if not email_field_name:
        return True
    queryset = user_class.objects.filter(**{email_field_name: email})
    return queryset.exists()


def is_user_email_field_unique():
    email_field_name = get_user_email_field_name()
    email_field = get_user_field_obj(email_field_name)
    return is_model_field_unique(email_field)


def get_user_email_field_name():
    return get_user_setting('EMAIL_FIELD')


def get_user_by_lookup_dict(
        lookup_dict, default=_RAISE_EXCEPTION, require_verified=True):
    verification_enabled = registration_settings.REGISTER_VERIFICATION_ENABLED
    verification_flag_field = get_user_setting('VERIFICATION_FLAG_FIELD')
    user_class = get_user_model()
    kwargs = {}
    kwargs.update(lookup_dict)
    if require_verified and verification_enabled and verification_flag_field:
        kwargs[verification_flag_field] = True
    try:
        user = get_object_or_404(user_class.objects.all(), **kwargs)
    except Http404:
        if default is _RAISE_EXCEPTION:
            raise UserNotFound() from None
        return default
    else:
        return user


def get_user_field_obj(name):
    user_class = get_user_model()
    return user_class._meta.get_field(name)  # pylint: disable=protected-access


def get_user_setting(name):
    setting_name = 'USER_{name}'.format(name=name)
    user_class = get_user_model()
    placeholder = object()
    value = getattr(user_class, name, placeholder)

    if value is placeholder:
        value = getattr(registration_settings, setting_name)

    return value


def build_initial_user(data: Dict[str, Any]) -> 'AbstractBaseUser':
    user_field_names = get_user_public_field_names(write_once=True)
    user_data = {}
    for field_name in user_field_names:
        if field_name in data:
            user_data[field_name] = data[field_name]
    user_class = get_user_model()
    return user_class(**user_data)


def get_user_field_names(
        allow_primary_key: bool = True, non_editable: bool = False):

    def not_in_seq(names):
        return lambda name: name not in names

    user_class = get_user_model()
    fields = user_class._meta.get_fields()  # pylint: disable=protected-access
    default_field_names = [f.name for f in fields
                           if (getattr(f, 'serialize', False) or
                               getattr(f, 'primary_key', False))]
    pk_field_names = [f.name for f in fields
                      if getattr(f, 'primary_key', False)]
    hidden_field_names = set(get_user_setting('HIDDEN_FIELDS'))
    hidden_field_names = hidden_field_names.union(['last_login', 'password'])
    public_field_names = get_user_setting('PUBLIC_FIELDS')
    editable_field_names = get_user_setting('EDITABLE_FIELDS')

    field_names = (public_field_names if public_field_names is not None
                   else default_field_names)
    if editable_field_names is None:
        editable_field_names = field_names

    editable_field_names = set(filter(not_in_seq(pk_field_names),
                                      editable_field_names))

    field_names = filter(not_in_seq(hidden_field_names), field_names)
    if not allow_primary_key:
        field_names = filter(not_in_seq(pk_field_names), field_names)

    if non_editable:
        field_names = filter(not_in_seq(editable_field_names), field_names)

    field_names = tuple(field_names)

    return field_names


def get_user_public_field_names(
        write_once: bool = False,
        read_only: bool = False) -> Tuple[str, ...]:

    fields = _get_user_default_fields()

    if read_only:
        field_names = _get_user_public_read_only_field_names(
            fields, write_once=write_once)
    else:
        field_names = _get_user_public_base_field_names(
            fields, write_once=write_once)

    return tuple(field_names)


def _get_user_public_read_only_field_names(
        fields: Iterable['UserField'],
        write_once: bool = False) -> List[str]:
    pk_name = _get_pk_name(fields)
    base_field_names = _get_user_public_base_field_names(
        fields, write_once=write_once)
    email_field_name = get_user_email_field_name()
    _editable_field_names = get_user_setting(
        'EDITABLE_FIELDS')  # type: Optional[Iterable[str]]
    editable_field_names = set_or_none(_editable_field_names)
    if write_once:
        excludes = {'last_login', pk_name}
    else:
        excludes = {'last_login', email_field_name, pk_name}
    field_names_rw = [f for f in base_field_names if f not in excludes]

    if not write_once and editable_field_names is not None:
        field_names_rw = [
            f for f in field_names_rw if f in editable_field_names]

    return [f for f in base_field_names if f not in field_names_rw]


def _get_user_public_base_field_names(
        fields: Iterable['UserField'],
        write_once: bool = False) -> List[str]:
    default_field_names = [f.name for f in fields]
    email_field_name = get_user_email_field_name()
    hidden_field_names = set(get_user_setting('HIDDEN_FIELDS'))
    _public_field_names = get_user_setting(
        'PUBLIC_FIELDS')  # type: Optional[Iterable[str]]
    public_field_names = set_or_none(_public_field_names)

    base_field_names = default_field_names
    if public_field_names is not None:
        allowed_field_names = public_field_names | {
            'password', email_field_name}
        base_field_names = [
            f for f in base_field_names if f in allowed_field_names]
    else:
        base_field_names = [
            f for f in base_field_names if f not in hidden_field_names]

    if not write_once:
        base_field_names = [f for f in base_field_names if f != 'password']

    return base_field_names


def _get_pk_name(fields: Iterable['UserField']) -> str:
    pk_names = [f.name for f in fields if getattr(f, 'primary_key', False)]
    if len(pk_names) != 1:
        raise ValueError('User model does not have one primary key')
    pk_name = pk_names[0]
    return pk_name


def _get_user_default_fields() -> List['UserField']:
    user_class = get_user_model()
    fields = user_class._meta.get_fields()  # pylint: disable=protected-access
    default_field_names = [
        f for f in fields
        if getattr(f, 'serialize', False) or getattr(f, 'primary_key', False)
    ]
    return default_field_names


def is_model_field_unique(field):
    return field.unique or field.primary_key


def get_object_or_404(queryset, *filter_args, **filter_kwargs):
    """
    Same as Django's standard shortcut, but make sure to also raise 404
    if the filter_kwargs don't match the required types.

    This function was copied from rest_framework.generics because of issue #36.
    """
    try:
        return _get_object_or_404(queryset, *filter_args, **filter_kwargs)
    except (TypeError, ValueError, ValidationError):
        raise Http404 from None
