import pytest

from rest_registration.exceptions import UserNotFound
from rest_registration.utils.users import (
    authenticate_by_login_data,
    get_user_field_names,
    get_user_public_field_names,
)
from tests.helpers.constants import USER_PASSWORD, USERNAME
from tests.helpers.settings import override_rest_registration_settings


@pytest.mark.parametrize(
    ("kwargs", "expected_fields"),
    [
        (
            {},
            {"id", "first_name", "last_name", "username", "email"},
        ),
        (
            {"allow_primary_key": False},
            {"first_name", "last_name", "username", "email"},
        ),
        (
            {"non_editable": True},
            {"id"},
        ),
        (
            {"allow_primary_key": False, "non_editable": True},
            set(),
        ),
    ],
)
def test_get_user_field_names(kwargs, expected_fields):
    assert set(get_user_field_names(**kwargs)) == expected_fields


@pytest.mark.parametrize(
    ("kwargs", "restreg_settings_override", "expected_fields"),
    [
        pytest.param(
            {"write_once": True},
            {},
            {"id", "first_name", "last_name", "username", "email", "password"},
            id="write-once",
        ),
        pytest.param(
            {"write_once": True, "read_only": True},
            {},
            {"id"},
            id="write-once,read-only",
        ),
        pytest.param(
            {},
            {},
            {"id", "first_name", "last_name", "username", "email"},
            id="write-many",
        ),
        pytest.param(
            {"read_only": True},
            {},
            {"id", "email"},
            id="write-many,read-only",
        ),
        pytest.param(
            {"write_once": True},
            {
                "USER_HIDDEN_FIELDS": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "user_permissions",
                    "groups",
                    "date_joined",
                )
            },
            {
                "id",
                "first_name",
                "last_name",
                "username",
                "email",
                "last_login",
                "password",
            },
            id="write-once;hidden-fields-set",
        ),
        pytest.param(
            {"write_once": True, "read_only": True},
            {
                "USER_HIDDEN_FIELDS": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "user_permissions",
                    "groups",
                    "date_joined",
                )
            },
            {"id", "last_login"},
            id="write-once,read-only;hidden-fields-set",
        ),
        pytest.param(
            {},
            {
                "USER_HIDDEN_FIELDS": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "user_permissions",
                    "groups",
                    "date_joined",
                )
            },
            {"id", "first_name", "last_name", "username", "email", "last_login"},
            id="write-many;hidden-fields-set",
        ),
        pytest.param(
            {"read_only": True},
            {
                "USER_HIDDEN_FIELDS": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "user_permissions",
                    "groups",
                    "date_joined",
                )
            },
            {"id", "email", "last_login"},
            id="write-many,read-only;hidden-fields-set",
        ),
        pytest.param(
            {"write_once": True},
            {"USER_PUBLIC_FIELDS": ["first_name", "last_name", "email"]},
            {"first_name", "last_name", "email", "password"},
            id="write-once;public-fields-set",
        ),
        pytest.param(
            {"write_once": True, "read_only": True},
            {"USER_PUBLIC_FIELDS": ["first_name", "last_name", "email"]},
            set(),
            id="write-once,read-only;public-fields-set",
        ),
        pytest.param(
            {},
            {"USER_PUBLIC_FIELDS": ["first_name", "last_name", "email"]},
            {"first_name", "last_name", "email"},
            id="write-many;public-fields-set",
        ),
        pytest.param(
            {"read_only": True},
            {"USER_PUBLIC_FIELDS": ["first_name", "last_name", "email"]},
            {"email"},
            id="write-many,read-only;public-fields-set",
        ),
        pytest.param(
            {"write_once": True},
            {"USER_EDITABLE_FIELDS": ["first_name", "last_name", "email"]},
            {"id", "first_name", "last_name", "username", "email", "password"},
            id="write-once;editable-fields-set",
        ),
        pytest.param(
            {"write_once": True, "read_only": True},
            {"USER_EDITABLE_FIELDS": ["first_name", "last_name", "email"]},
            {"id"},
            id="write-once,read-only;editable-fields-set",
        ),
        pytest.param(
            {},
            {"USER_EDITABLE_FIELDS": ["first_name", "last_name", "email"]},
            {"id", "first_name", "last_name", "username", "email"},
            id="write-many;editable-fields-set",
        ),
        pytest.param(
            {"read_only": True},
            {"USER_EDITABLE_FIELDS": ["first_name", "last_name", "email"]},
            {"id", "username", "email"},
            id="write-many,read-only;editable-fields-set",
        ),
    ],
)
def test_get_user_public_field_names(
    kwargs, restreg_settings_override, expected_fields
):
    with override_rest_registration_settings(restreg_settings_override):
        assert set(get_user_public_field_names(**kwargs)) == expected_fields


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(
            {
                "login": USERNAME,
            },
            id="missing password",
        ),
        pytest.param(
            {
                "login": USERNAME,
                "password": USER_PASSWORD + "blah",
            },
            id="invalid password",
        ),
        pytest.param(
            {
                "username": USERNAME,
                "password": USER_PASSWORD + "blah",
            },
            id="username but invalid password",
        ),
    ],
)
def test_authenticate_by_login_data_fails(user, data):
    with pytest.raises(UserNotFound):
        authenticate_by_login_data(data)
