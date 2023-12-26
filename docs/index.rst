.. Django-REST-Registration documentation master file, created by
   sphinx-quickstart on Mon Nov 19 01:44:40 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Django REST Registration's documentation!
====================================================

User registration REST API, based on Django-REST-Framework.

.. toctree::
    :maxdepth: 2

    install
    quickstart
    detailed_configuration/index


Requirements
------------

-   Django (2.0+, 3.0+, 4.0+) and Django-REST-Framework (3.3+)
-   Python 3.6 or higher (no Python 2 support!)


Features
--------

-   Supported views:

    -   registration (sign-up) with verification
    -   login/logout (sign-in), session- or token-based
    -   user profile (retrieving / updating)
    -   reset password
    -   change password
    -   register (change) e-mail

-   Views are compatible with
    `django-rest-swagger <https://github.com/marcgibbons/django-rest-swagger>`__
-   Views can be authenticated via session or auth token
-   Modeless (uses the user defined by ``settings.AUTH_USER_MODEL`` and
    also uses `cryptographic
    signing <https://docs.djangoproject.com/en/dev/topics/signing/>`__
    instead of profile models)
-   Uses `password
    validation <https://docs.djangoproject.com/en/dev/topics/auth/passwords/#password-validation>`__
-   Heavily tested (Above 98% code coverage)


Current limitations
-------------------

-   Supports only one email per user (as user model field)
-   No JWT support (but you can use it along libraries like
    `django-rest-framework-simplejwt <https://github.com/davesque/django-rest-framework-simplejwt>`__)


Indices and tables
------------------

*   :ref:`genindex`
*   :ref:`search`
