import pytest
from django.test.utils import override_settings
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import force_authenticate

from tests.helpers.api_views import (
    assert_response_is_bad_request,
    assert_response_is_forbidden,
    assert_response_is_ok,
)
from tests.helpers.constants import USER_PASSWORD, USERNAME
from tests.helpers.views import ViewProvider


@pytest.mark.parametrize(
    "password_confirm",
    [
        pytest.param(True, id="password_confirm"),
        pytest.param(False, id="password_no_confirm"),
    ],
)
def test_ok(
    settings_minimal,
    user,
    response_factory,
    old_password,
    new_password,
    password_confirm,
):
    data = {
        "old_password": old_password,
        "password": new_password,
    }
    response = response_factory(
        user,
        data,
        password_confirm_copy=password_confirm,
        password_confirm_case=password_confirm,
    )
    assert_response_is_ok(response)
    user.refresh_from_db()
    assert user.check_password(new_password)


@pytest.mark.parametrize(
    "password_confirm",
    [
        pytest.param(True, id="password_confirm"),
        pytest.param(False, id="password_no_confirm"),
    ],
)
def test_no_auth_fail(
    settings_minimal,
    user,
    response_factory,
    old_password,
    new_password,
    password_confirm,
):
    data = {
        "old_password": old_password,
        "password": new_password,
    }
    response = response_factory(
        None,
        data,
        password_confirm_copy=password_confirm,
        password_confirm_case=password_confirm,
    )
    assert_response_is_forbidden(response)
    user.refresh_from_db()
    assert user.check_password(old_password)


@pytest.mark.parametrize(
    "password_confirm",
    [
        pytest.param(True, id="password_confirm"),
        pytest.param(False, id="password_no_confirm"),
    ],
)
@pytest.mark.parametrize(
    ("data", "expected_errors"),
    [
        pytest.param(
            {
                "old_password": "blah",
                "password": "newtestpassword",
            },
            {
                "old_password": [
                    ErrorDetail(string="Old password is not correct", code="invalid")
                ]
            },
            id="invalid_old_password",
        ),
        pytest.param(
            {
                "old_password": USER_PASSWORD,
                "password": "xqx",
            },
            {
                "password": [
                    ErrorDetail(
                        string=(
                            "This password is too short."
                            " It must contain at least 8 characters."
                        ),
                        code="password_too_short",
                    )
                ]
            },
            id="short_password",
        ),
        pytest.param(
            {
                "old_password": USER_PASSWORD,
                "password": "password",
            },
            {
                "password": [
                    ErrorDetail(
                        string="This password is too common.",
                        code="password_too_common",
                    )
                ]
            },
            id="common_password",
        ),
        pytest.param(
            {
                "old_password": USER_PASSWORD,
                "password": "234665473425345",
            },
            {
                "password": [
                    ErrorDetail(
                        string="This password is entirely numeric.",
                        code="password_entirely_numeric",
                    )
                ]
            },
            id="numeric_password",
        ),
        pytest.param(
            {
                "old_password": USER_PASSWORD,
                "password": USERNAME,
            },
            {
                "password": [
                    ErrorDetail(
                        string="The password is too similar to the username.",
                        code="password_too_similar",
                    )
                ]
            },
            id="password_same_as_username",
        ),
    ],
)
def test_wrong_password_fail(
    settings_minimal,
    user,
    response_factory,
    password_confirm,
    data,
    expected_errors,
):
    response = response_factory(
        user,
        data,
        password_confirm_copy=password_confirm,
        password_confirm_case=password_confirm,
    )
    assert_response_is_bad_request(response)
    if expected_errors:
        assert response.data == expected_errors
    user.refresh_from_db()
    assert user.check_password(USER_PASSWORD)


def test_missing_confirm_fail(
    settings_minimal,
    user,
    response_factory,
    old_password,
    new_password,
):
    response = response_factory(
        user,
        {
            "old_password": old_password,
            "password": new_password,
        },
        password_confirm_copy=False,
        password_confirm_case=True,
    )

    assert_response_is_bad_request(response)
    user.refresh_from_db()
    assert user.check_password(old_password)


def test_invalid_confirm_fail(
    settings_minimal,
    user,
    response_factory,
    old_password,
    new_password,
):
    response = response_factory(
        user,
        {
            "old_password": old_password,
            "password": new_password,
            "password_confirm": new_password + "a",
        },
        password_confirm_copy=False,
        password_confirm_case=True,
    )

    assert_response_is_bad_request(response)
    user.refresh_from_db()
    assert user.check_password(old_password)


@pytest.fixture
def response_factory(
    api_view_provider,
    api_factory,
):
    def _get_resp(
        auth_user, data, password_confirm_copy=True, password_confirm_case=True
    ):
        req_data = {}
        req_data.update(data)
        if password_confirm_copy:
            req_data["password_confirm"] = req_data["password"]
        request = api_factory.create_post_request(req_data)
        if auth_user is not None:
            force_authenticate(request, user=auth_user)
        if password_confirm_case:
            response = api_view_provider.view_func(request)
        else:
            with override_settings(
                REST_REGISTRATION={
                    "CHANGE_PASSWORD_SERIALIZER_PASSWORD_CONFIRM": False,
                }
            ):
                response = api_view_provider.view_func(request)
        return response

    return _get_resp


@pytest.fixture
def old_password(password_change):
    return password_change.old_value


@pytest.fixture
def new_password(password_change):
    return password_change.new_value


@pytest.fixture
def api_view_provider():
    return ViewProvider("change-password")
