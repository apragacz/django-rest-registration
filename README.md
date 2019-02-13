# Django-REST-Registration

[![Build Status](https://travis-ci.org/apragacz/django-rest-registration.svg?branch=master)](https://travis-ci.org/apragacz/django-rest-registration)
[![Codecov Coverage](https://img.shields.io/codecov/c/github/apragacz/django-rest-registration/master.svg)](https://codecov.io/github/apragacz/django-rest-registration?branch=master)
[![PyPi Version](https://img.shields.io/pypi/v/django-rest-registration.svg)](https://pypi.python.org/pypi/django-rest-registration/)
[![Documentation Status](https://readthedocs.org/projects/django-rest-registration/badge/?version=latest)](https://django-rest-registration.readthedocs.io/en/latest/?badge=latest)

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
* Heavily tested (Above 98% code coverage)


## Current limitations

* Supports only one email per user (as model field)
* Heavily based on Django (1.10+, 2.0+) and Django-REST-Framework (3.3+)
* Python3 only
* No JWT support


## Installation

You can install `django-rest-registration` lastest version via pip:

    pip install django-rest-registration

Or install directly from source via GitHub:

    pip install git+https://github.com/apragacz/django-rest-registration

Then, you should add it to the `INSTALLED_APPS` so the app templates
for notification emails can be accessed:

```python
INSTALLED_APPS=(
    ...

    'rest_registration',
)
```
After that, you can use the urls in your urlconfig, for instance (using new Django 2.x syntax):

```python
api_urlpatterns = [
    ...

    path('accounts/', include('rest_registration.api.urls')),
]


urlpatterns = [
    ...

    path('api/v1/', include(api_urlpatterns)),
]
```

In Django 1.x you can use old `url` instead of `path`.


## Configuration

You can configure `django-rest-registraton` using the `REST_REGISTRATION`
setting in your django settings (similarly to `django-rest-framework`).

Below is sample, minimal config you can provide in your django settings which will satisfy the system checks:

```python
REST_REGISTRATION = {
    'REGISTER_VERIFICATION_ENABLED': False,

    'RESET_PASSWORD_VERIFICATION_URL': 'https://frontend-host/reset-password/',

    'REGISTER_EMAIL_VERIFICATION_ENABLED': False,

    'VERIFICATION_FROM_EMAIL': 'no-reply@example.com',
}
```

However, the preferred base configuration would be:

```python
REST_REGISTRATION = {
    'REGISTER_VERIFICATION_URL': 'https://frontend-host/verify-user/',
    'RESET_PASSWORD_VERIFICATION_URL': 'https://frontend-host/reset-password/',
    'REGISTER_EMAIL_VERIFICATION_URL': 'https://frontend-host/verify-email/',

    'VERIFICATION_FROM_EMAIL': 'no-reply@example.com',
}
```

The frontend urls are not provided by the library but should be provided
by the user of the library, because `django-rest-registration` is frontend-agnostic.
The frontend urls will receive parameters as GET query and should pass
them to corresponding REST API views via HTTP POST request.

Let's explain it by example:

we're assuming that the `django-rest-registration` views are served at
https://backend-host/api/v1/accounts/.
The frontend endpoint https://frontend-host/verify-email/ would receive
following GET parameters:
* `user_id`
* `email`
* `timestamp`
* `signature`

and then it should perform AJAX request to https://backend-host/api/v1/accounts/verify-email/
via HTTP POST with following JSON payload:

```javascript
{
    "user_id": "<user id>",
    "email": "<email>",
    "timestamp": "<timestamp>",
    "signature": "<signature>"
}
```

and then show a message to the user depending on the response
from backend server.

## Configuration options

You can modify following keys in `REST_REGISTRATION` dictionary.
The default values are shown below:

```python
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

    'REGISTER_SERIALIZER_CLASS': 'rest_registration.api.serializers.DefaultRegisterUserSerializer',
    'REGISTER_SERIALIZER_PASSWORD_CONFIRM': True,

    'REGISTER_VERIFICATION_ENABLED': True,
    'REGISTER_VERIFICATION_PERIOD': datetime.timedelta(days=7),
    'REGISTER_VERIFICATION_URL': None,
    'REGISTER_VERIFICATION_EMAIL_TEMPLATES': {
        'subject':  'rest_registration/register/subject.txt',
        'body':  'rest_registration/register/body.txt',
    },

    'LOGIN_SERIALIZER_CLASS': 'rest_registration.api.serializers.DefaultLoginSerializer',
    'LOGIN_AUTHENTICATE_SESSION': None,
    'LOGIN_RETRIEVE_TOKEN': None,

    'RESET_PASSWORD_VERIFICATION_PERIOD': datetime.timedelta(days=1),
    'RESET_PASSWORD_VERIFICATION_URL': None,
    'RESET_PASSWORD_VERIFICATION_ONE_TIME_USE': False,
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

    'CHANGE_PASSWORD_SERIALIZER_PASSWORD_CONFIRM': True,

    'PROFILE_SERIALIZER_CLASS': 'rest_registration.api.serializers.DefaultUserProfileSerializer',

    'VERIFICATION_FROM_EMAIL': None,
    'VERIFICATION_REPLY_TO_EMAIL': None,
    'VERIFICATION_EMAIL_HTML_TO_TEXT_CONVERTER': 'rest_registration.utils.convert_html_to_text_preserving_urls',

    'SUCCESS_RESPONSE_BUILDER': 'rest_registration.utils.build_default_success_response',
}
```

The `USER_*` fields can be set directly in the user class
(specified by `settings.AUTH_USER_MODEL`) without using
the `USER_` prefix (`EMAIL_FIELD`, etc.). These settings will override these
provided in `settings.REST_REGISTRATION`.

You can send the verification emails as HTML, by specifying `html_body` instead of `body`; for example:

```python
REST_REGISTRATION = {
    ...

    'REGISTER_VERIFICATION_EMAIL_TEMPLATES': {
        'subject':  'rest_registration/register/subject.txt',
        'html_body':  'rest_registration/register/body.html',
    },

    ...
}
```

This will automatically create fallback plain text message from the HTML. If you want to have custom fallback messsage you can also provide separate template for text:

```python
REST_REGISTRATION = {
    ...

    'REGISTER_VERIFICATION_EMAIL_TEMPLATES': {
        'subject':  'rest_registration/register/subject.txt',
        'text_body':  'rest_registration/register/body.text',
        'html_body':  'rest_registration/register/body.html',
    },

    ...
}
```
