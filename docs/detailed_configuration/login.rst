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


List of settings
----------------

These settings can be used to configure login views.
You should add them as keys (with values)
to your ``settings.REST_REGISTRATION`` dict.

.. jinja:: detailed_configuration__login
   :file: detailed_configuration/settings_fields.j2
