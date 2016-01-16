from django.contrib import auth
from rest_framework import serializers
from rest_framework.decorators import api_view

from rest_registration.exceptions import BadRequest
from rest_registration.settings import settings as registration_settings
from rest_registration.utils import get_user_model_class, get_ok_response


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField()


@api_view(['POST'])
def login(request):
    '''
    ---
    serializer: LoginSerializer
    '''
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.data

    User = get_user_model_class()
    login_fields = (registration_settings.USER_LOGIN_FIELDS
                    or getattr(User, 'LOGIN_FIELDS', None)
                    or [User.USERNAME_FIELD])

    for field_name in login_fields:
        kwargs = {
            field_name: data['login'],
            'password': data['password'],
        }
        user = auth.authenticate(**kwargs)
        if user:
            break

    if not user:
        raise BadRequest('Login or password invalid.')

    auth.login(request, user)

    return get_ok_response('Login successful')


@api_view(['POST'])
def logout(request):
    '''
    Logs out the user. returns an error if the user is not
    authenticated.
    '''
    if not request.user.is_authenticated():
        raise BadRequest('Not logged in')

    auth.logout(request)

    return get_ok_response('Logout successful')
