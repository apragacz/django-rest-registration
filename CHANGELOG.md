# Changelog


## Version 0.7

### v0.7.3

*   Use user backend field when available (#196)


### v0.7.2

*   Add `REGISTER_FLOW_ENABLED` setting (#186)


### v0.7.1

*   Make email sending replaceable (#183)
*   Drop Django 1.x support from requirements


### v0.7.0

*   Add Django 4.x support (#172)
*   Drop official support for Django 1.x
*   Drop official support for Python 3.4


## Version 0.6

### v0.6.5

*   Add `LOGIN_DEFAULT_SESSION_AUTHENTICATION_BACKEND` setting (#168)


### v0.6.4

*   Add `VERIFICATION_TEMPLATE_RENDERER` setting (#157)
*   Extract error codes from validate_password (#160)


### v0.6.3

*   Fix `USER_LOGIN_FIELDS` issue (#141)


### v0.6.2

*   Improve email templates system check (#116)
*   Add `VERIFICATION_TEMPLATES_SELECTOR` setting (#133)
*   Update deprecation warnings and documentation (#138)


### v0.6.1

*   Fix Django 3.2 system checks issue (#134)


### v0.6.0

*   Add a check for `SEND_RESET_PASSWORD_LINK_SERIALIZER_USE_EMAIL` (#92)
*   Remove typing ignores (#109)
*   Deprecate `DefaultRegisterEmailSerializer.get_email()` method (#95)
*   Add `SEND_RESET_PASSWORD_LINK_USER_FINDER` (#94)
*   Add `USE_NON_FIELD_ERRORS_KEY_FROM_DRF_SETTINGS` (#125)
*   Use `get_user_public_field_names()` instead of `get_user_field_names()`
*   Add Brazilian Portuguese (pt_BR) translation (#122)
*   Add `LOGIN_AUTHENTICATOR` function setting (#51)
*   Move password validation to reset password serializer (#110)


## Version 0.5


### v0.5.6

*   Add `'RESET_PASSWORD_SERIALIZER_PASSWORD_CONFIRM'` setting key (issue #108)
*   Auth Token manager support (issue #98)



### v0.5.5

*   Fixed password validation to support users with foreign keys (issue #106)
*   Added `'NOT_AUTHENTICATED_PERMISSION_CLASSES'` setting (PR #105)

### v0.5.4

*   Re-enable Django 3.0 and DRF 3.10 support (issue #70)
*   Put the code for sending the register verification email in separate
*   send_register_verification_email_notification (issue #100)



### v0.5.3

*   Add `'RESET_PASSWORD_FAIL_WHEN_USER_NOT_FOUND'` setting key (issue #81)
*   Add login fields unique system check (issue #91)
*   Limit Django to <3.0 (due to some incompatibility issues - limit will
*   be lifted in 0.6.*)
*   Add Makefile (issue #88)
*   Add French message translation (pull request #85)
*   Add Contributing Guidelines (issue #64)
*   Introduce various test code refactors


### v0.5.2

*   Resolve issue #77: Allow using DRR without templates setup
*   Fix issue #79: do not create user when sending verification fails
*   Fix issue #83: Support change to already existing e-mail in the DB
*   Detect whether user email field is unique. If yes, then send "e-mail
*   already exists" notification instead of verification one.
*   Also, perform a check just before changing the e-mail to avoid
*   integrity errors.
*   Fix issue #68
*   Add `VERIFICATION_TEMPLATE_CONTEXT_BUILDER` settings key
*   Fix invalid config in README


### v0.5.1

*   Allow `TokenAuthentication` subclasses (pull request #74)
*   Fix issue #52: Check whether valid Django authentication backend is being used
*   Add Change email verification signal (pull request #69)
*   Set more restrictive linters: pylint with improved config, flake8-comprehensions plugin added
*   Force to use Django REST Framework version lower than 3.10 (this limitation will be removed in 0.6.0)


### v0.5.0

*   Fix critical security issue with misusing the Django Signer API. Thanks for @peterthomassen for finding the bug!
*   Resolve issue #57: Pass request in serializer context in all views
*   Add signals for injecting logic in user registration


## Version 0.4


### v0.4.5

*   Resolve issue #48: Allowing to use custom user field for verification
*   Resolve issue #46
*   Add `SEND_RESET_PASSWORD_LINK_SERIALIZER_USE_EMAIL` setting
*   Resolve issue #50: add customizable send reset password link serializer
*   Fix reset password in case user is unverified and one-time use is enabled


### v0.4.4

*   Resolve issue #44
*   Resolve issue #45


### v0.4.3

*   Update documentation and README


### v0.4.2

*   Resolve issue #39
*   Resolve issue #40


### v0.4.1

*   Resolve #36
*   Add improvements in the documentation


### v0.4.0

*   Upgrade to major version


## Version 0.3

### v0.3.14

*   Fix: Add permission classes in case of endpoints using anonymous users.
*   Add `RESET_PASSWORD_VERIFICATION_ENABLED`
*   Add more liberal checks for `VERIFICATION_FROM_EMAIL`
*   Add implementation details concerning settings fields and NestedSettings


### v0.3.13

*   Resolve issue #29: Add `RESET_PASSWORD_VERIFICATION_ONE_TIME_USE` setting
*   Drop support of Django 1.10, add explicit support of Django 2.1


### v0.3.12

*   Resolve #22: Send HTML verification emails
*   Resolve #23: Add `CHANGE_PASSWORD_SERIALIZER_PASSWORD_CONFIRM` setting


### v0.3.9

*   Resolve #21: Add `REGISTER_OUTPUT_SERIALIZER_CLASS` setting
*   Resolve #12: Add verification_redirects Django app
*   Resolve #19: Add `LOGIN_SERIALIZER_CLASS` rest_registration setting


### v0.3.8

*   Allow only verified users to register email or reset password
*   Resolve issue #16: added `revoke_token` option
*   Use py.test and tox for testing
*   Fix issues with renderers: `_get_serializer` passes the params to serializer class
*   Fix url patterns


### v0.3.7

*   Fix issue #8 - Schemas not showing up in django-rest-swagger
*   Fix issue #9 - Register view was able to create user without email with
    email verification enabled


### v0.3.6

*   Add app name and view names in urls.py


### v0.3.5

*   Add `REGISTER_SERIALIZER_PASSWORD_CONFIRM` field to `REST_REGISTRATION` settings
    to potentially disable `password_confirm` field
    in `DefaultRegisterUserSerializer` (issue #2, #3).


### v0.3.4

*   Fix unnecessary verification URL escaping in email templates
*   Fix sending verification URL to new email instead to the old one in `register_email`


### v0.3.3

*   Add missing template files in sdist package


### v0.3.0

*   Fix problems with tests after changes introduced in Django 1.11 (Issue #1)
*   Fix is_authenticated attribute change introduced in Django 1.10, which breaks
    compatibility in Django 2.0


## Version 0.2

### v0.2.1

*   Limit this version to using Django 1.9 - 1.10


### v0.2.0

*   Add password validation
*   Add configurable success response builder
*   Add system checks for registration settings
*   Use different salt in each `DataSigner` subclass
*   Fix for read-only fields in `DefaultUserProfileSerializer`
