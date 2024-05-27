import pytest
from rest_framework.test import force_authenticate

from tests.helpers.api_views import assert_response_is_ok
from tests.helpers.constants import USERNAME
from tests.helpers.views import ViewProvider


def test_retrieve_ok(
    settings_minimal,
    user,
    api_view_provider,
    api_factory,
):
    request = api_factory.create_get_request()
    force_authenticate(request, user=user)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    user_id = response.data["id"]
    assert user_id == user.id


def test_patch_names_ok(
    settings_minimal,
    user,
    api_view_provider,
    api_factory,
):
    request = api_factory.create_patch_request(
        {
            "first_name": "Donald",
            "last_name": "Knuth",
        }
    )
    force_authenticate(request, user=user)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    user_id = response.data["id"]
    user.refresh_from_db()
    assert user_id == user.id
    assert user.username == USERNAME
    assert user.first_name == "Donald"
    assert user.last_name == "Knuth"


def test_patch_username_ok(
    settings_minimal,
    user,
    api_view_provider,
    api_factory,
):
    old_first_name = user.first_name
    old_last_name = user.last_name
    request = api_factory.create_patch_request(
        {
            "username": "dknuth",
        }
    )
    force_authenticate(request, user=user)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    user_id = response.data["id"]
    user.refresh_from_db()
    assert user_id == user.id
    assert user.username == "dknuth"
    assert user.first_name == old_first_name
    assert user.last_name == old_last_name


def test_patch_id_nochange(
    settings_minimal,
    user,
    api_view_provider,
    api_factory,
):
    old_user_id = user.id
    old_first_name = user.first_name
    old_last_name = user.last_name
    request = api_factory.create_patch_request(
        {
            "id": old_user_id + 1,
        }
    )
    force_authenticate(request, user=user)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    user_id = response.data["id"]
    user.refresh_from_db()
    assert user_id == user.id
    assert user.id == old_user_id
    assert user.username == USERNAME
    assert user.first_name == old_first_name
    assert user.last_name == old_last_name


@pytest.fixture
def api_view_provider():
    return ViewProvider("profile")


@pytest.fixture
def old_email(email_change):
    return email_change.old_value


@pytest.fixture
def new_email(email_change):
    return email_change.new_value


def test_update_email_via_profile(
    settings_with_register_email_verification,
    user,
    old_email,
    new_email,
    api_view_provider,
    api_factory,
):
    request = api_factory.create_patch_request(
        {
            "email": new_email,
        }
    )
    force_authenticate(request, user=user)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    user.refresh_from_db()
    assert user.email == old_email
