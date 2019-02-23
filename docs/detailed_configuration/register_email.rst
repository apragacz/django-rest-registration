Email Registration
==================

API Views
---------

There are two views used in the email registration / change workflow:

.. _register-email-view:

register-email
~~~~~~~~~~~~~~

.. autofunction:: rest_registration.api.views.register_email

.. _verify-email-view:

verify-email
~~~~~~~~~~~~

.. autofunction:: rest_registration.api.views.verify_email

List of settings
----------------

These settings can be used to configure email registration workflow.
You should add them as keys (with values)
to your ``settings.REST_REGISTRATION`` dict.

.. jinja:: detailed_configuration__register_email
   :file: detailed_configuration/settings_fields.j2
