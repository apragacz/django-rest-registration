from django.test import Client
from django.test.utils import override_settings

from tests.helpers.testcases import BaseViewTestCase


@override_settings(
    ROOT_URLCONF='tests.unit_tests.contrib.verification_redirects.default_urls',
)
class ViewTestCase(BaseViewTestCase):
    APP_NAME = 'rest_registration.contrib.verification_redirects'

    def setUp(self):
        super().setUp()
        self.client = Client()
