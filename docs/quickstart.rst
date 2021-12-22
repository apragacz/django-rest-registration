.. _quickstart:

Quickstart
==========

Assuming you have installed Django REST Registration
(more installation options can be found :ref:`here<installation>`):

::

    pip install django-rest-registration

you should add it to the ``INSTALLED_APPS`` in your Django settings
so the app templates for notification emails can be accessed:

.. code:: python

    INSTALLED_APPS=(
        ...

        'rest_registration',
    )

After that, you can use the urls in your Django urlconfig, for instance:

.. code:: python

    api_urlpatterns = [
        ...

        path('accounts/', include('rest_registration.api.urls')),
    ]


    urlpatterns = [
        ...

        path('api/v1/', include(api_urlpatterns)),
    ]

In this example, the Django REST Registration API views will be served under
``https://your-backend-host/api/v1/accounts/``.
Obviously, you can choose different URI path than ``api/v1/accounts/``,
depending on your preferences.


Minimal Configuration
---------------------

You can configure Django REST Registration using the
``REST_REGISTRATION`` setting in your Django settings (similarly to
Django REST Framework).

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

The minimal configuration is very limited, because it:

-   disables e-mail verification for new users
    (:ref:`register-verification-enabled-setting`), which means that the user
    can set the e-mail to one not belonging to him/her,
-   disables e-mail verification for e-mail change
    (:ref:`register-email-verification-enabled-setting`), which again means
    that the user can change the e-mail to one not belonging to him/her,
-   disabled verification for reset password
    (:ref:`reset-password-verification-enabled-setting`) which basically
    disables the ability to reset password.

Therefore, the preferred base configuration would be:

.. code:: python

    REST_REGISTRATION = {
        'REGISTER_VERIFICATION_URL': 'https://frontend-host/verify-user/',
        'RESET_PASSWORD_VERIFICATION_URL': 'https://frontend-host/reset-password/',
        'REGISTER_EMAIL_VERIFICATION_URL': 'https://frontend-host/verify-email/',

        'VERIFICATION_FROM_EMAIL': 'no-reply@example.com',
    }


You need to replace ``'https://frontend-host/reset-password/'``
with the URL on your frontend which will be pointed in the "reset password"
e-mail. This also applies to the other verification urls above.
You also need also to replace ``'no-reply@example.com'`` with the
e-mail address which will be used as the sender of the verification e-mails.

In case when any verification is enabled, (which is the default!)
your Django application needs to be
`properly configured so it can send e-mails <https://docs.djangoproject.com/en/dev/topics/email/>`__.

The frontend urls are not provided by the library but should be provided
by the user of the library (you), because Django REST Registration is
frontend-agnostic.

If you want to understand how the verification workflows work and how the
provided frontend endpoints should work please read:

-   :ref:`Register
    verification workflow <register-verification-workflow>`
-   :ref:`Register e-mail
    verification workflow <register-email-verification-workflow>`
-   :ref:`Reset password
    verification workflow <reset-password-verification-workflow>`

In most cases, the frontend urls should receive parameters as GET
query and should pass them to corresponding REST API views via HTTP POST
request. The one exception is reset password workflow, where the page under
frontend endpoint should also gather the new password from the user and send
it along other data via HTTP POST to the REST API endpoint.
