import pytest

from rest_registration.utils.users import (
    UserPublicFieldsType,
    get_user_field_names,
    get_user_public_field_names
)
from tests.helpers.settings import override_rest_registration_settings


@pytest.mark.parametrize('kwargs,expected_fields', [
    (
        {},
        {'id', 'first_name', 'last_name', 'username', 'email'},
    ),
    (
        {'allow_primary_key': False},
        {'first_name', 'last_name', 'username', 'email'},
    ),
    (
        {'non_editable': True},
        {'id'},
    ),
    (
        {'allow_primary_key': False, 'non_editable': True},
        set(),
    ),
])
def test_get_user_field_names(kwargs, expected_fields):
    assert set(get_user_field_names(**kwargs)) == expected_fields


@pytest.mark.parametrize(
    'fields_type,restreg_settings_override,expected_fields',
    [
        pytest.param(
            UserPublicFieldsType.READ_ONLY,
            {},
            {
                'id', 'first_name', 'last_name', 'username', 'email',
                'last_login',
            },
            id='read-only',
        ),
        pytest.param(
            UserPublicFieldsType.READ_WRITE,
            {},
            {'first_name', 'last_name', 'username'},
            id='read-write',
        ),
        pytest.param(
            UserPublicFieldsType.WRITE_ONCE,
            {},
            {'first_name', 'last_name', 'username', 'email', 'password'},
            id='write-once',
        ),
        pytest.param(
            UserPublicFieldsType.READ_ONLY,
            {'USER_PUBLIC_FIELDS': ['first_name', 'last_name', 'email']},
            {'first_name', 'last_name', 'email'},
            id='read-only;public-fields-set',
        ),
        pytest.param(
            UserPublicFieldsType.READ_WRITE,
            {'USER_PUBLIC_FIELDS': ['first_name', 'last_name', 'email']},
            {'first_name', 'last_name'},
            id='read-write;public-fields-set',
        ),
        pytest.param(
            UserPublicFieldsType.WRITE_ONCE,
            {'USER_PUBLIC_FIELDS': ['first_name', 'last_name', 'email']},
            {'first_name', 'last_name', 'email', 'password'},
            id='write-once;public-fields-set',
        ),
        pytest.param(
            UserPublicFieldsType.READ_ONLY,
            {'USER_EDITABLE_FIELDS': ['first_name', 'last_name', 'email']},
            {
                'id', 'first_name', 'last_name', 'username', 'email',
                'last_login',
            },
            id='read-only;editable-fields-set',
        ),
        pytest.param(
            UserPublicFieldsType.READ_WRITE,
            {'USER_EDITABLE_FIELDS': ['first_name', 'last_name', 'email']},
            {'first_name', 'last_name'},
            id='read-write;editable-fields-set',
        ),
        pytest.param(
            UserPublicFieldsType.WRITE_ONCE,
            {'USER_EDITABLE_FIELDS': ['first_name', 'last_name', 'email']},
            {'first_name', 'last_name', 'username', 'email', 'password'},
            id='write-once;editable-fields-set',
        ),
    ],
)
def test_get_user_public_field_names(
        fields_type, restreg_settings_override, expected_fields):
    with override_rest_registration_settings(restreg_settings_override):
        assert set(get_user_public_field_names(fields_type)) == expected_fields
