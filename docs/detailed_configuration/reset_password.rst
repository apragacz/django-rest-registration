Reset password
==============

API Views
---------

There are two views used in the login workflow:

.. _send-reset-password-link-view:

send-reset-password-link
~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: rest_registration.api.views.send_reset_password_link

.. _reset-password-view:

reset-password
~~~~~~~~~~~~~~

.. autofunction:: rest_registration.api.views.reset_password

List of settings
----------------

These settings can be used to configure reset password workflow.
You should add them as keys (with values)
to your ``settings.REST_REGISTRATION`` dict.

.. jinja:: detailed_configuration__reset_password
   :file: detailed_configuration/settings_fields.j2
