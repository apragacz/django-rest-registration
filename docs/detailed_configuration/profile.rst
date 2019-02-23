User profile
============

API Views
---------

There is one view used for retrieving user profile and applying changes:

.. _profile-view:

profile
~~~~~~~

.. autofunction:: rest_registration.api.views.profile

Default serializers
-------------------

.. _default-user-profile-serializer:

DefaultUserProfileSerializer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: rest_registration.api.serializers.DefaultUserProfileSerializer

List of settings
----------------

These settings can be used to configure user profile view.
You should add them as keys (with values)
to your ``settings.REST_REGISTRATION`` dict.

.. jinja:: detailed_configuration__profile
   :file: detailed_configuration/settings_fields.j2
