Registration
============

API Views
---------

There are two views used in the registration workflow:

.. autofunction:: rest_registration.api.views.register

.. autofunction:: rest_registration.api.views.verify_registration

Assuming that the `django-rest-registration` views are served at
https://backend-host/api/v1/accounts/
then the ``register``, ``verify_registration`` views are served as:

* https://backend-host/api/v1/accounts/register/
* https://backend-host/api/v1/accounts/verify-registration/

accordingly.

List of settings
----------------

These settings can be used to configure registration workflow.
You should add them as keys (with values)
to your ``settings.REST_REGISTRATION`` dict.

.. jinja:: detailed_configuration__register
   :file: detailed_configuration/settings_fields.j2
