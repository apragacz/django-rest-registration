User configuration
==================

List of settings
----------------

These settings can be used to configure how the user model
(specified by ``settings.AUTH_USER_MODEL``) should be used.
You should add them as keys (with values)
to your ``settings.REST_REGISTRATION`` dict.

The ``USER_*`` fields can be set directly in the user class (specified
by ``settings.AUTH_USER_MODEL``) without using the ``USER_`` prefix
(``EMAIL_FIELD``, etc.). These settings will override these provided in
``settings.REST_REGISTRATION``.

.. jinja:: detailed_configuration__user
   :file: detailed_configuration/settings_fields.j2
