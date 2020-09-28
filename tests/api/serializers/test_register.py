import pytest

from rest_registration.settings import registration_settings


@pytest.fixture()
def serializer():
    serializer_class = registration_settings.REGISTER_SERIALIZER_CLASS
    return serializer_class(data={})


def test_generated_fields(settings_with_register_verification, serializer):
    field_names = set(serializer.get_fields())
    assert field_names == {
        'id', 'username', 'first_name', 'last_name', 'email',
        'password', 'password_confirm',
    }


def test_simple_email_based_user_generated_fields(
        settings_with_register_verification,
        settings_with_simple_email_based_user,
        serializer):
    field_names = set(serializer.get_fields())

    assert field_names == {'id', 'email', 'password', 'password_confirm'}


def test_no_password_generated_fields(
        settings_with_register_verification,
        settings_with_register_no_confirm,
        serializer):
    field_names = set(serializer.get_fields())
    assert field_names == {
        'id', 'username', 'first_name', 'last_name', 'email', 'password',
    }
