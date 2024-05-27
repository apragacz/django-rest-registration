import pytest
from django.conf import settings
from django.test.utils import override_settings


@pytest.fixture
def settings_with_verification_redirects_urls():
    with override_settings(
        ROOT_URLCONF="tests.unit_tests.contrib.verification_redirects.default_urls",
    ):
        yield settings


@pytest.fixture
def app_name():
    return "rest_registration.contrib.verification_redirects"
