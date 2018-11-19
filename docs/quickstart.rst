Quickstart
==========

Then, you should add it to the ``INSTALLED_APPS`` so the app templates
for notification emails can be accessed:

.. code:: python

    INSTALLED_APPS=(
        ...

        'rest_registration',
    )

After that, you can use the urls in your urlconfig, for instance (using
new Django 2.x syntax):

.. code:: python

    api_urlpatterns = [
        ...

        path('accounts/', include('rest_registration.api.urls')),
    ]


    urlpatterns = [
        ...

        path('api/v1/', include(api_urlpatterns)),
    ]

In Django 1.x you can use old ``url`` instead of ``path``.


Minimal Configuration
---------------------

You can configure ``django-rest-registraton`` using the
``REST_REGISTRATION`` setting in your django settings (similarly to
``django-rest-framework``).

If you don't do that, Django system checks will inform you
about invalid configuration.

Below is sample, minimal config you can provide in your Django settings
which will satisfy the system checks:

.. code:: python

    REST_REGISTRATION = {
        'REGISTER_VERIFICATION_ENABLED': False,
        'REGISTER_EMAIL_VERIFICATION_ENABLED': False,
        'RESET_PASSWORD_VERIFICATION_ENABLED': False,
    }


Preferred Configuration
-----------------------

The minimal configuration is very limited, because it disables verification
for new users (``REGISTER_VERIFICATION_ENABLED``), verification
for e-mail change (``REGISTER_EMAIL_VERIFICATION_ENABLED``) and
verification for reset password  (``RESET_PASSWORD_VERIFICATION_ENABLED``).
However, the preferred base configuration would be:

.. code:: python

    REST_REGISTRATION = {
        'REGISTER_VERIFICATION_URL': 'https://frontend-host/verify-user/',
        'RESET_PASSWORD_VERIFICATION_URL': 'https://frontend-host/reset-password/',
        'REGISTER_EMAIL_VERIFICATION_URL': 'https://frontend-host/verify-email/',

        'VERIFICATION_FROM_EMAIL': 'no-reply@example.com',
    }


You need to replace ``'https://frontend-host/reset-password/'``
with the URL on your frontend which will be pointed in the "reset password"
e-mail. You also need also to replace ``'no-reply@example.com'`` with the
e-mail address which will be used as the sender of the reset e-mail.

The frontend urls are not provided by the library but should be provided
by the user of the library, because ``django-rest-registration`` is
frontend-agnostic. The frontend urls will receive parameters as GET
query and should pass them to corresponding REST API views via HTTP POST
request.

Let's explain it by example:

we're assuming that the ``django-rest-registration`` views are served at
https://backend-host/api/v1/accounts/. The frontend endpoint
https://frontend-host/verify-email/ would receive following GET
parameters:

- ``user_id``
- ``email``
- ``timestamp``
- ``signature``

and then it should perform AJAX request to
https://backend-host/api/v1/accounts/verify-email/ via HTTP POST with
following JSON payload:

.. code:: javascript

    {
        "user_id": "<user id>",
        "email": "<email>",
        "timestamp": "<timestamp>",
        "signature": "<signature>"
    }

and then show a message to the user depending on the response from
backend server.
