import pytest

from rest_registration.utils.users import (
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
    'kwargs,restreg_settings_override,expected_fields',
    [
        pytest.param(
            {'write_once': True},
            {},
            {
                'id', 'first_name', 'last_name', 'username', 'email',
                'last_login', 'password',
            },
            id='write-once',
        ),
        pytest.param(
            {'write_once': True, 'read_only': True},
            {},
            {'id', 'last_login'},
            id='write-once,read-only',
        ),
        pytest.param(
            {},
            {},
            {
                'id', 'first_name', 'last_name', 'username', 'email',
                'last_login',
            },
            id='write-many',
        ),
        pytest.param(
            {'read_only': True},
            {},
            {'id', 'email', 'last_login'},
            id='write-many,read-only',
        ),

        pytest.param(
            {'write_once': True},
            {'USER_PUBLIC_FIELDS': ['first_name', 'last_name', 'email']},
            {'first_name', 'last_name', 'email', 'password'},
            id='write-once;public-fields-set',
        ),
        pytest.param(
            {'write_once': True, 'read_only': True},
            {'USER_PUBLIC_FIELDS': ['first_name', 'last_name', 'email']},
            set(),
            id='write-once,read-only;public-fields-set',
        ),
        pytest.param(
            {},
            {'USER_PUBLIC_FIELDS': ['first_name', 'last_name', 'email']},
            {'first_name', 'last_name', 'email'},
            id='write-many;public-fields-set',
        ),
        pytest.param(
            {'read_only': True},
            {'USER_PUBLIC_FIELDS': ['first_name', 'last_name', 'email']},
            {'email'},
            id='write-many,read-only;public-fields-set',
        ),

        pytest.param(
            {'write_once': True},
            {'USER_EDITABLE_FIELDS': ['first_name', 'last_name', 'email']},
            {
                'id', 'first_name', 'last_name', 'username', 'email',
                'last_login', 'password',
            },
            id='write-once;editable-fields-set',
        ),
        pytest.param(
            {'write_once': True, 'read_only': True},
            {'USER_EDITABLE_FIELDS': ['first_name', 'last_name', 'email']},
            {'id', 'last_login'},
            id='write-once,read-only;editable-fields-set',
        ),
        pytest.param(
            {},
            {'USER_EDITABLE_FIELDS': ['first_name', 'last_name', 'email']},
            {
                'id', 'first_name', 'last_name', 'username', 'email',
                'last_login',
            },
            id='write-many;editable-fields-set',
        ),
        pytest.param(
            {'read_only': True},
            {'USER_EDITABLE_FIELDS': ['first_name', 'last_name', 'email']},
            {'id', 'username', 'last_login', 'email'},
            id='write-many,read-only;editable-fields-set',
        ),
    ],
)
def test_get_user_public_field_names(
        kwargs, restreg_settings_override, expected_fields):
    with override_rest_registration_settings(restreg_settings_override):
        assert set(get_user_public_field_names(**kwargs)) == expected_fields
