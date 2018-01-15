# Django-REST-Registration

User registration REST API, based on django-rest-framework.

WARNING: `django-rest-registration` is only Python 3 compatible.


## Features

* Supported views:
    * registration (sign-up) with verification
    * login/logout (sign-in), session- or token-based
    * user profile (retrieving / updating)
    * reset password
    * change password
    * register (change) e-mail
* Views are compatible with [django-rest-swagger](https://github.com/marcgibbons/django-rest-swagger)
* Views can be authenticated via session or auth token
* Modeless (uses the user defined by `settings.AUTH_USER_MODEL` and also uses [cryptographic signing](https://docs.djangoproject.com/en/dev/topics/signing/) instead of profile models)
* Uses [password validation](https://docs.djangoproject.com/en/dev/topics/auth/passwords/#password-validation)
* Heavily tested (Above 99% code coverage)


## Current limitations

* Supports only one email per user (as model field)
* Heavily based on Django (1.10+, 2.0+) an Django-REST-Framework (3.3+)
* Python3 only
* No JWT support


## Installation

You can install `django-rest-registration` lastest version via pip:

    pip install django-rest-registration

Or install directly from source via GitHub:

    pip install git+https://github.com/szopu/django-rest-registration

Then, you should add it to the `INSTALLED_APPS` so the app templates
for notification emails can be accessed:

    INSTALLED_APPS=(
        ...

        'rest_registration',
    ),

After that, you can use the urls in your urlconfig, for instance (using new Django 2.x syntax):

    api_urlpatterns = [
        ...

        path('accounts/', include('rest_registration.api.urls')),
    ]


    urlpatterns = [
        ...

        path('api/v1/', include(api_urlpatterns)),
    ]


In Django 1.x you can use old `url` instead of `path`.


## Configuration

You can configure `django-rest-registraton` using the `REST_REGISTRATION`
setting in your django settings (similarly to `django-rest-framework`).

Below is sample, minimal config you can provide in your django settings which will satisfy the system checks:

    REST_REGISTRATION = {
        'REGISTER_VERIFICATION_ENABLED': False,

        'RESET_PASSWORD_VERIFICATION_URL': '/reset-password/',

        'REGISTER_EMAIL_VERIFICATION_ENABLED': False,

        'VERIFICATION_FROM_EMAIL': 'no-reply@example.com',
    }


The default values are:

    REST_REGISTRATION = {
        'USER_LOGIN_FIELDS': None,
        'USER_HIDDEN_FIELDS': (
            'is_active',
            'is_staff',
            'is_superuser',
            'user_permissions',
            'groups',
            'date_joined',
        ),
        'USER_PUBLIC_FIELDS': None,
        'USER_EMAIL_FIELD': 'email',

        'USER_VERIFICATION_FLAG_FIELD': 'is_active',

        'REGISTER_SERIALIZER_CLASS': (
            'rest_registration.api.serializers.DefaultRegisterUserSerializer'),

        'REGISTER_VERIFICATION_ENABLED': True,
        'REGISTER_VERIFICATION_PERIOD': datetime.timedelta(days=7),
        'REGISTER_VERIFICATION_URL': None,
        'REGISTER_VERIFICATION_EMAIL_TEMPLATES': {
            'subject':  'rest_registration/register/subject.txt',
            'body':  'rest_registration/register/body.txt',
        },

        'LOGIN_AUTHENTICATE_SESSION': None,
        'LOGIN_RETRIEVE_TOKEN': None,

        'RESET_PASSWORD_VERIFICATION_PERIOD': datetime.timedelta(days=1),
        'RESET_PASSWORD_VERIFICATION_URL': None,
        'RESET_PASSWORD_VERIFICATION_EMAIL_TEMPLATES': {
            'subject': 'rest_registration/reset_password/subject.txt',
            'body': 'rest_registration/reset_password/body.txt',
        },

        'REGISTER_EMAIL_VERIFICATION_ENABLED': True,
        'REGISTER_EMAIL_VERIFICATION_PERIOD': datetime.timedelta(days=7),
        'REGISTER_EMAIL_VERIFICATION_URL': None,
        'REGISTER_EMAIL_VERIFICATION_EMAIL_TEMPLATES': {
            'subject':  'rest_registration/register_email/subject.txt',
            'body':  'rest_registration/register_email/body.txt',
        },

        'PROFILE_SERIALIZER_CLASS': (
            'rest_registration.api.serializers.DefaultUserProfileSerializer'),

        'VERIFICATION_FROM_EMAIL': None,
        'VERIFICATION_REPLY_TO_EMAIL': None,

        'SUCCESS_RESPONSE_BUILDER': (
            'rest_registration.utils.build_default_success_response')

    }

The `USER_*` fields can be set directly in the user class
(specified by `settings.AUTH_USER_MODEL`) without using
the `USER_` prefix (`EMAIL_FIELD`, etc.). These settings will override these
provided in `settings.REST_REGISTRATION`.
