import pytest
from django.test.utils import override_settings

from rest_registration.utils.nested_settings import NestedSettings


def test_user_settings(settings_defaults):
    user_settings = {
        'A': 1,
    }
    settings = NestedSettings(
        user_settings, settings_defaults, (), 'NESTED_TEST_SETTING')

    assert settings.A == 1
    assert settings.B == 3


@override_settings(
    REST_REGISTRATION={
        'A': 5,
    }
)
def test_django_settings(settings_defaults):
    settings = NestedSettings(
        None, settings_defaults, (), 'REST_REGISTRATION')
    assert settings.A == 5
    assert settings.B == 3


@pytest.fixture
def settings_defaults():
    return {
        'A': 2,
        'B': 3,
    }
