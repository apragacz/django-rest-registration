from rest_framework import status
from rest_framework.test import force_authenticate

from rest_registration.api.views import profile
from .base import APIViewTestCase


REGISTER_VERIFICATION_URL = '/verify-account/'


class ProfileViewTestCase(APIViewTestCase):
    USERNAME = 'e.dijkstra'
    FIRST_NAME = 'Edsger'
    LAST_NAME = 'Dijkstra'
    PASSWORD = 'testpassword'

    def setUp(self):
        super().setUp()
        self.user = self.create_test_user(
            username=self.USERNAME,
            first_name=self.FIRST_NAME,
            last_name=self.LAST_NAME,
            password=self.PASSWORD,
        )
        self.user_id = self.user.id

    def test_retrieve_ok(self):
        request = self.factory.get('')
        force_authenticate(request, user=self.user)
        response = profile(request)
        self.assert_valid_response(response, status.HTTP_200_OK)
        user_id = response.data['id']
        self.assertEqual(user_id, self.user.id)

    def _get_valid_patch_response(self, data):
        request = self.factory.patch('', data)
        force_authenticate(request, user=self.user)
        response = profile(request)
        self.assert_valid_response(response, status.HTTP_200_OK)
        user_id = response.data['id']
        self.assertEqual(user_id, self.user.id)
        return response

    def test_patch_names_ok(self):
        response = self._get_valid_patch_response({
            'first_name': 'Donald',
            'last_name': 'Knuth',
        })
        self.assert_response_is_ok(response)
        self.user.refresh_from_db()
        self.assertEqual(self.user.id, self.user_id)
        self.assertEqual(self.user.username, self.USERNAME)
        self.assertEqual(self.user.first_name, 'Donald')
        self.assertEqual(self.user.last_name, 'Knuth')

    def test_patch_username_ok(self):
        response = self._get_valid_patch_response({
            'username': 'dknuth',
        })
        self.assert_response_is_ok(response)
        self.user.refresh_from_db()
        self.assertEqual(self.user.id, self.user_id)
        self.assertEqual(self.user.username, 'dknuth')
        self.assertEqual(self.user.first_name, self.FIRST_NAME)
        self.assertEqual(self.user.last_name, self.LAST_NAME)

    def test_patch_id_nochange(self):
        response = self._get_valid_patch_response({
            'id': 10,
        })
        self.assert_response_is_ok(response)
        self.user.refresh_from_db()
        self.assertEqual(self.user.id, self.user_id)
        self.assertEqual(self.user.username, self.USERNAME)
        self.assertEqual(self.user.first_name, self.FIRST_NAME)
        self.assertEqual(self.user.last_name, self.LAST_NAME)
