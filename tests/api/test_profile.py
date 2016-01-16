from django.test.utils import override_settings
from rest_framework import status
from rest_framework.test import force_authenticate

from rest_registration.api.views import profile
from .base import APIViewTestCase


REGISTER_VERIFICATION_URL = '/verify-account/'


class ProfileViewTestCase(APIViewTestCase):

    def test_ok(self):
        user = self.create_test_user()
        request = self.factory.get('')
        force_authenticate(request, user=user)
        response = profile(request)
        self.assert_valid_response(response, status.HTTP_200_OK)
        user_id = response.data['id']
        self.assertEqual(user_id, user.id)
