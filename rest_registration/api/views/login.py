from django.contrib import auth
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.settings import api_settings

from rest_registration.exceptions import BadRequest
from rest_registration.settings import registration_settings
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

    user_class = get_user_model_class()
    login_fields = (registration_settings.USER_LOGIN_FIELDS
                    or getattr(user_class, 'LOGIN_FIELDS', None)
                    or [user_class.USERNAME_FIELD])

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

    if should_authenticate_session():
        auth.login(request, user)

    extra_data = {}

    if should_retrieve_token():
        extra_data['token'], _ = Token.objects.get_or_create(user=user)

    return get_ok_response('Login successful', extra_data=extra_data)


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


def should_authenticate_session():
    result = registration_settings.LOGIN_AUTHENTICATE_SESSION
    if result is None:
        result = rest_auth_has_class('SessionAuthentication')
    return result


def should_retrieve_token():
    result = registration_settings.LOGIN_RETRIEVE_TOKEN
    if result is None:
        result = rest_auth_has_class('TokenAuthentication')
    return result


def rest_auth_has_class(class_name):
    import_str = 'rest_framework.authentication.{}'.format(class_name)
    return import_str in api_settings.DEFAULT_AUTHENTICATION_CLASSES
