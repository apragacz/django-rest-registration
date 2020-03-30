# Django REST Registration

[![Build Status](https://travis-ci.org/apragacz/django-rest-registration.svg?branch=master)](https://travis-ci.org/apragacz/django-rest-registration)
[![Codecov Coverage](https://codecov.io/gh/apragacz/django-rest-registration/branch/master/graphs/badge.svg?branch=master)](https://codecov.io/github/apragacz/django-rest-registration?branch=master)
[![PyPi Version](https://badge.fury.io/py/django-rest-registration.svg)](https://pypi.python.org/pypi/django-rest-registration/)
[![Documentation Status](https://readthedocs.org/projects/django-rest-registration/badge/?version=latest)](https://django-rest-registration.readthedocs.io/en/latest/?badge=latest)

User registration REST API, based on Django REST Framework.

Full documentation for the project is available at [https://django-rest-registration.readthedocs.io/](https://django-rest-registration.readthedocs.io/).

## Requirements

* Django (1.10+, 2.0+, 3.0+) and Django-REST-Framework (3.3+)
* Python 3.4 or higher (no Python 2 support!)

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
* No JWT support (but you can use it along libraries like [django-rest-framework-simplejwt](https://github.com/davesque/django-rest-framework-simplejwt))


## Installation & Configuration

You can [install](https://django-rest-registration.readthedocs.io/en/latest/install.html)
Django REST Registration latest version via pip:

    pip install django-rest-registration

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

You can configure Django REST Registraton using the `REST_REGISTRATION`
setting in your Django settings (similarly to Django REST Framework).

Below is sample, minimal config you can provide in your django settings which will satisfy the system checks:

```python
REST_REGISTRATION = {
    'REGISTER_VERIFICATION_ENABLED': False,
    'RESET_PASSWORD_VERIFICATION_ENABLED': False,
    'REGISTER_EMAIL_VERIFICATION_ENABLED': False,
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
by the user of the library, because Django REST Registration is frontend-agnostic.
The frontend urls will receive parameters as GET query and should pass
them to corresponding REST API views via HTTP POST request.

In case when any verification is enabled (which is the default!),
your Django application needs to be
[properly configured so it can send e-mails](https://docs.djangoproject.com/en/dev/topics/email/).

You can read more about basic configuration
[here](https://django-rest-registration.readthedocs.io/en/latest/quickstart.html).

You can read more about detailed configuration
[here](https://django-rest-registration.readthedocs.io/en/latest/detailed_configuration/).

## Configuration options

You can find all `REST_REGISTRATION` configuration options
[here](https://django-rest-registration.readthedocs.io/en/latest/detailed_configuration/all_settings.html).
