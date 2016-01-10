from django.test.utils import override_settings
from rest_framework import status

from rest_registration.api.register_views import register
from rest_registration.api.serializers import get_register_serializer_class
from .base import APIViewTestCase


class RegisterViewTestCase(APIViewTestCase):

    def test_register_serializer_ok(self):
        serializer_class = get_register_serializer_class()
        serializer = serializer_class(data={})
        field_names = {f for f in serializer.get_fields()}
        self.assertEqual(
            field_names,
            {'username', 'first_name', 'last_name', 'email',
             'password', 'password_confirm'},
        )

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_VERIFICATION_URL': '/verify-account/'
        }
    )
    def test_register_ok(self):
        username = 'testusername'
        password = 'testpassword'
        request = self.factory.post('', {
            'username': username,
            'password': password,
            'password_confirm': password,
        })
        with self.assert_mail_sent():
            response = register(request)
        self.assert_valid_response(response, status.HTTP_201_CREATED)
        user_id = response.data['id']
        user = self.user_class.objects.get(id=user_id)
        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_active)
