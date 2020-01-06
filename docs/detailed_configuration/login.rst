Login
=====

API Views
---------

There are two views used in the login workflow:

.. _login-view:

login
~~~~~

.. autofunction:: rest_registration.api.views.login

.. _logout-view:

logout
~~~~~~

.. autofunction:: rest_registration.api.views.logout

Default serializers
-------------------

.. _default-login-serializer:

DefaultLoginSerializer
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: rest_registration.api.serializers.DefaultLoginSerializer
   :members:


Custom token generation
-----------------------

One can replace :ref:`auth-token-manager-class-setting`
with his / her own class, which should inherit from / implement
``rest_registration.auth_token_managers.AbstractAuthTokenManager``.
The ``AbstractAuthTokenManager`` class has following methods:

.. autoclass:: rest_registration.auth_token_managers.AbstractAuthTokenManager
    :members:

If you're using custom authentication class, you should set
:ref:`login-retrieve-token-setting` explicitly to ``True`` as token
retrieval can be automatically turned on only when
``rest_framework.authentication.TokenAuthentication`` (or a subclass) is used.

List of settings
----------------

These settings can be used to configure login views.
You should add them as keys (with values)
to your ``settings.REST_REGISTRATION`` dict.

.. jinja:: detailed_configuration__login
   :file: detailed_configuration/settings_fields.j2
