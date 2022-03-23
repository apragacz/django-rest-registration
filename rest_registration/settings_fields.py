import datetime
from collections import OrderedDict, namedtuple
from textwrap import dedent

_Field = namedtuple('_Field', [
    'name',
    'default',
    'help',
    'import_string',
])


class Field(_Field):

    def __new__(
            cls, name, *,
            default=None,
            help=None,  # pylint: disable=redefined-builtin
            import_string=False):
        return super().__new__(
            cls, name=name, default=default,
            help=help, import_string=import_string)


USER_SETTINGS_FIELDS = [
    Field(
        'USER_LOGIN_FIELDS',
    ),
    Field(
        'USER_HIDDEN_FIELDS',
        default=(
            'last_login',
            'is_active',
            'is_staff',
            'is_superuser',
            'user_permissions',
            'groups',
            'date_joined',
        ),
    ),
    Field(
        'USER_PUBLIC_FIELDS',
    ),
    Field(
        'USER_EDITABLE_FIELDS',
    ),
    Field(
        'USER_EMAIL_FIELD',
        default='email',
    ),
    Field(
        'USER_VERIFICATION_ID_FIELD',
        default='pk',
        help=dedent("""\
            Field used in verification, as part of signed data.

            The given field should uniquely identify the user. This means that
            using any user field which could change over time
            (``email``, ``username``) is NOT recommended.
            """),
    ),
    Field(
        'USER_VERIFICATION_FLAG_FIELD',
        default='is_active',
    ),
]

REGISTER_SETTINGS_FIELDS = [
    Field(
        'REGISTER_FLOW_ENABLED',
        default=True,
        help=dedent("""\
            If enabled, then users are able to register (create new account).

            One can disable it if for instance accounts should not be registered
            by external users but rather should be created only by admin user.
            """),
    ),
    Field(
        'REGISTER_SERIALIZER_CLASS',
        default='rest_registration.api.serializers.DefaultRegisterUserSerializer',  # noqa: E501,
        import_string=True,
        help=dedent("""\
            The serializer used by :ref:`register-view` endpoint.
            It is used to validate the input data and save (create)
            the newly registered user. You can use your custom serializer
            to customise validation logic and the way the user is created
            in the database.
            """),
    ),
    Field(
        'REGISTER_SERIALIZER_PASSWORD_CONFIRM',
        default=True,
        help=dedent("""\
            Used by ``DefaultRegisterUserSerializer``.
            If ``True``, the serializer requires
            additional field ``password_confirm`` which value should be
            the same as the value of ``password`` field.

            It may be useful to disable it if you perform password confirmation
            at the frontend level.
            """),
    ),

    Field(
        'REGISTER_OUTPUT_SERIALIZER_CLASS',
        default='rest_registration.api.serializers.DefaultUserProfileSerializer',  # noqa: E501,
        import_string=True,
        help=dedent("""\
            The default serializer used by register endpoint.
            It is used output the data associated with
            the newly registered user. You can use your custom serializer
            to customise the output representation of the user.
            """),
    ),

    Field(
        'REGISTER_VERIFICATION_ENABLED',
        default=True,
        help=dedent("""\
            If enabled, then newly registered user will not
            be verified (user field specified by
            :ref:`user-verification-flag-field-setting` will be false),
            and verification e-mail with activation link
            will be sent to the user email (specified by ``USER_EMAIL_FIELD``).
            """),
    ),
    Field(
        'REGISTER_VERIFICATION_EMAIL_SENDER',
        default='rest_registration.verification_notifications.send_register_verification_email_notification',  # noqa: E501
        import_string=True,
        help=dedent("""\
            By default the email sender function will work with the build-in email
            sending mechanism.

            You can handle email sending all by yourself by overriding this setting.
            """),
    ),
    Field(
        'REGISTER_VERIFICATION_PERIOD',
        default=datetime.timedelta(days=7),
        help=dedent("""\
            Specifies how long the activation link will be valid.
            """),
    ),
    Field(
        'REGISTER_VERIFICATION_URL',
        help=dedent("""\
            Frontend URL to which the query parameters will be appended
            to create the activation link for newly registered user.
            """),
    ),
    Field('REGISTER_VERIFICATION_ONE_TIME_USE', default=False),
    Field(
        'REGISTER_VERIFICATION_EMAIL_TEMPLATES',
        default={
            'subject': 'rest_registration/register/subject.txt',
            'body': 'rest_registration/register/body.txt',
        },
        help=dedent("""\
            Directory of templates used to generate the verification email.
            There are separate templates for email body and subject.
            If you want to generate html emails please refer to
            :ref:`html-email`.
            """),
    ),
    Field(
        'REGISTER_VERIFICATION_AUTO_LOGIN',
        default=False,
        help=dedent("""\
            Specifies whether a user will be logged in automatically when they
            verify their registration.
            """),
    ),
]

LOGIN_SETTINGS_FIELDS = [
    Field(
        'LOGIN_SERIALIZER_CLASS',
        default='rest_registration.api.serializers.DefaultLoginSerializer',  # noqa: E501
        import_string=True,
    ),
    Field(
        'LOGIN_AUTHENTICATOR',
        default='rest_registration.utils.users.authenticate_by_login_data',
        import_string=True,
        help=dedent("""\
            By default the login authenticator function will use
            :ref:`user-login-fields-setting` setting to extract the login field
            from the validated serializer data either by using the 'login' key
            or the specific login field name(s) (e.g. 'username', 'email').

            You can change that behavior by overriding this setting.

            The authenticator function receives these parameters as
            positional arguments:

            *   ``data`` - the validated data from the login serializer.

            and these parameters as keyword arguments:

            *   ``serializer`` - the source login serializer which generated
                the input data. This parameter could be dropped in the future,
                so it should be retrieved via ``kwargs.get()`` instead be named
                directly.

            If the user cannot be found, the function should raise ``UserNotFound``
            exception (from ``rest_registration.exceptions``).
            """),
    ),
    Field('LOGIN_AUTHENTICATE_SESSION'),
    Field('LOGIN_RETRIEVE_TOKEN'),
    Field(
        'AUTH_TOKEN_MANAGER_CLASS',
        default='rest_registration.auth_token_managers.RestFrameworkAuthTokenManager',  # noqa: E501
        import_string=True,
        help=dedent("""\
            The token manager class used by :ref:`login-view`
            and :ref:`logout-view` which provides an interface for providing
            and optionally revoking the token.
            The class should inherit from
            ``rest_registration.token_managers.AbstractTokenManager``.
            """)
    ),
    Field(
        'LOGIN_DEFAULT_SESSION_AUTHENTICATION_BACKEND',
        default='django.contrib.auth.backends.ModelBackend',
        help=dedent("""\
            This setting allows to override the backend used in the login function.

            It may be useful if Django ``AUTHENTICATION_BACKENDS`` setting
            does contain multiple values.

            The value must be a dotted import path string.
            """),
    )
]
RESET_PASSWORD_SETTINGS_FIELDS = [
    Field(
        'SEND_RESET_PASSWORD_LINK_SERIALIZER_CLASS',
        default='rest_registration.api.serializers.DefaultSendResetPasswordLinkSerializer',  # noqa: E501,
        import_string=True,
        help=dedent("""\
            The serializer used by :ref:`send-reset-password-link-view`
            endpoint. You can use your custom serializer
            to customise validation logic and perform additonal checks.
            Please remember that it should implement ``get_user_or_none``
            method which is used to obtain the user matching the criteria.
            """)
    ),
    Field(
        'SEND_RESET_PASSWORD_LINK_USER_FINDER',
        default='rest_registration.utils.users.find_user_by_by_send_reset_password_link_data',  # noqa: E501
        import_string=True,
        help=dedent("""\
            By default the user finder function will use
            :ref:`user-login-fields-setting` setting to extract the login field
            from the validated serializer data either by using the 'login' key
            or the specific login field name(s) (e.g. 'username', 'email').
            You can change that behavior by overriding this setting.

            The user finder function receives these parameters as
            positional arguments:

            *   ``data`` - the validated data from the send reset pasword
                link serializer.

            and these parameters as keyword arguments:

            *   ``serializer`` - the source send reset password link serializer
                which generated the input data. This parameter could be dropped
                in the future, so it should be retrieved via ``kwargs.get()``
                instead be named directly.

            If the user cannot be found, the function should raise ``UserNotFound``
            exception (from ``rest_registration.exceptions``).
            """)
    ),
    Field(
        'SEND_RESET_PASSWORD_LINK_SERIALIZER_USE_EMAIL',
        default=False,
        help=dedent("""\
            Used specifically by ``DefaultSendResetPasswordLinkSerializer``.

            If ``True``, use e-mail field instead of login fields to find
            the user who should receive the reset password link.
            """)
    ),
    Field(
        'RESET_PASSWORD_FAIL_WHEN_USER_NOT_FOUND',
        default=True,
        help=dedent("""\
            If ``True``, then reveal that the user does not exist
            while reset password link is being sent by signaling an error.
            """)
    ),
    Field('RESET_PASSWORD_VERIFICATION_ENABLED', default=True),
    Field(
        'RESET_PASSWORD_VERIFICATION_EMAIL_SENDER',
        default='rest_registration.verification_notifications.send_reset_password_verification_email_notification',  # noqa: E501
        import_string=True,
        help=dedent("""\
            By default the email sender function will work with the build-in email
            sending mechanism.

            You can handle email sending all by yourself by overriding this setting.
            """),
    ),
    Field(
        'RESET_PASSWORD_VERIFICATION_PERIOD',
        default=datetime.timedelta(days=1),
    ),
    Field('RESET_PASSWORD_VERIFICATION_URL'),
    Field('RESET_PASSWORD_VERIFICATION_ONE_TIME_USE', default=False),
    Field(
        'RESET_PASSWORD_VERIFICATION_EMAIL_TEMPLATES',
        default={
            'subject': 'rest_registration/reset_password/subject.txt',
            'body': 'rest_registration/reset_password/body.txt',
        },
    ),
    Field(
        'RESET_PASSWORD_SERIALIZER_PASSWORD_CONFIRM',
        default=False,
        help=dedent("""\
            Used by ``ResetPasswordSerializer``.
            If ``True``, the serializer requires
            additional field ``password_confirm`` which value should be
            the same as the value of ``password`` field.

            It may be useful to disable it (this is currently the default)
            if you perform password confirmation
            at the frontend level.
            """),
    ),
]
REGISTER_EMAIL_SETTINGS_FIELDS = [
    Field(
        'REGISTER_EMAIL_SERIALIZER_CLASS',
        default='rest_registration.api.serializers.DefaultRegisterEmailSerializer',  # noqa: E501
        import_string=True,
        help=dedent("""\
            The serializer used by :ref:`register-email-view` endpoint.
            It is used to validate the input data and obtain new e-mail.
            You can use your custom serializer
            to customise validation logic. The important part is that it should contain
            ``email`` field.
            """),
    ),
    Field('REGISTER_EMAIL_VERIFICATION_ENABLED', default=True),
    Field(
        'REGISTER_EMAIL_VERIFICATION_EMAIL_SENDER',
        default='rest_registration.verification_notifications.send_register_email_verification_email_notification',  # noqa: E501
        import_string=True,
        help=dedent("""\
            By default the email sender function will work with the build-in email
            sending mechanism.

            You can handle email sending all by yourself by overriding this setting.
            """),
    ),
    Field(
        'REGISTER_EMAIL_VERIFICATION_PERIOD',
        default=datetime.timedelta(days=7),
    ),
    Field('REGISTER_EMAIL_VERIFICATION_URL'),
    Field(
        'REGISTER_EMAIL_VERIFICATION_EMAIL_TEMPLATES',
        default={
            'subject': 'rest_registration/register_email/subject.txt',
            'body': 'rest_registration/register_email/body.txt',
        },
    ),
]

GLOBAL_VERIFICATION_SETTINGS_FIELDS = [
    Field('VERIFICATION_FROM_EMAIL'),
    Field('VERIFICATION_REPLY_TO_EMAIL'),
    Field(
        'VERIFICATION_EMAIL_HTML_TO_TEXT_CONVERTER',
        default='rest_registration.utils.html.convert_html_to_text_preserving_urls',  # noqa: E501
        import_string=True,
    ),
    Field(
        'VERIFICATION_URL_BUILDER',
        default='rest_registration.utils.verification.build_default_verification_url',  # noqa: E501
        import_string=True,
        help=dedent("""\
            The builder function receives the ``signer`` object and construct
            the url using ``signer.get_base_url()``
            and ``signer.get_signed_data()``. The default url builder will use
            the base url and append the signed data as HTTP GET query string.
            It is be solely up to the implementer of custom builder function
            to encode the signed values properly in the URL.
            """),
    ),
    Field(
        'VERIFICATION_TEMPLATE_CONTEXT_BUILDER',
        default='rest_registration.utils.verification.build_default_template_context',  # noqa: E501
        import_string=True,
        help=dedent("""\
            The builder function receives these parameters as
            positional arguments:

            *   ``user`` - the user which is to be notified.
            *   ``user_address`` - the user address, which can be the
                user e-mail, phone number, etc.
            *   ``data`` - dictionary; in most cases it contains only
                one entry, which is the ``param_signer``
                under ``'param_signer'`` key. The implementer of the
                custom builder function should be aware that the contents
                of the dictionary are dynamic and write defensive code
                to account that.

            and these parameters as keyword arguments:

            *   ``notification_type`` - value of
                ``rest_registration.notifications.enums.NotificationType``
                enum.
            *   ``notification_method`` - value of
                ``rest_registration.notifications.enums.NotificationMethod``
                enum. Currently there is only one choice which is
                ``NotificationMethod.EMAIL``.

            It is possible that in the future, additional keyword arguments
            may be added. Therefore the implementer
            of the custom builder function should take account of that,
            for instance by adding ``**kwargs`` in the signature
            of the function.
            """),
    ),
    Field(
        'VERIFICATION_TEMPLATE_RENDERER',
        default='rest_registration.utils.verification.default_render_template',
        import_string=True,
        help=dedent("""\
            The builder function receives these parameters as
            positional arguments:

            *   ``template_config_data`` - dictionary; data is populated by
                function set with :ref:`verification-templates-selector-setting`
                setting.
            *   ``context`` - dictionary; data is populated by function set
                with :ref:`verification-template-context-builder-setting`
                setting.

            Function should return an instance of
            ``rest_registration.utils.verification.EmailTemplateRenderResult``

            It is possible that in the future, additional keyword arguments
            may be added. Therefore the implementer
            of the custom builder function should take account of that,
            for instance by adding ``**kwargs`` in the signature
            of the function.
        """),
    ),
    Field(
        'VERIFICATION_TEMPLATES_SELECTOR',
        default='rest_registration.utils.verification.select_default_templates',
        import_string=True,
        help=dedent("""\
            By default, the verification templates selector function will use
            templates defined by these settings:

            *   :ref:`register-verification-email-templates-setting`
            *   :ref:`register-email-verification-email-templates-setting`
            *   :ref:`reset-password-verification-email-templates-setting`

            depending on the notification type (register,
            registere email, reset password).
            You can change that behavior by overriding this setting.

            The verification template selector function receives these parameters
            as keyword arguments:

            *   ``request`` - the request which is source of sending given verification.
            *   ``user`` - the user which is to be notified.
            *   ``notification_type`` - value of
                ``rest_registration.notifications.enums.NotificationType``
                enum.
            *   ``notification_method`` - value of
                ``rest_registration.notifications.enums.NotificationMethod``

            It is possible that in the future, additional keyword arguments
            may be added. Therefore the implementer
            of the custom selector function should take account of that,
            for instance by adding ``**kwargs`` in the signature
            of the function.

            The verification template selector should raise
            ``VerificationTemplatesNotFound`` exception when no matching templates
            were found. In that case, Django REST Registration will fall back
            to the default behavior (described above).
            """),
    ),
]

CHANGE_PASSWORD_SETTINGS_FIELDS = [
    Field('CHANGE_PASSWORD_SERIALIZER_PASSWORD_CONFIRM', default=True),
]

PROFILE_SETTINGS_FIELDS = [
    Field(
        'PROFILE_SERIALIZER_CLASS',
        default='rest_registration.api.serializers.DefaultUserProfileSerializer',  # noqa: E501
        import_string=True,
    ),
]

MISC_SETTINGS_FIELDS = [
    Field(
        'SUCCESS_RESPONSE_BUILDER',
        default='rest_registration.utils.responses.build_default_success_response',  # noqa: E501
        import_string=True,
    ),
    Field(
        'USE_NON_FIELD_ERRORS_KEY_FROM_DRF_SETTINGS',
        default=False,
        help=dedent("""\
            If ``True``, the base API exception class will wrap the detail
            string message (or message list) into a dictionary with a key
            defined by ``REST_FRAMEWORK['NON_FIELD_ERRORS_KEY']``.
            """),
    ),
]

PERMISSIONS_SETTINGS_FIELDS = [
    Field(
        'NOT_AUTHENTICATED_PERMISSION_CLASSES',
        default=['rest_framework.permissions.AllowAny'],
        import_string=True,
        help=dedent("""\
            This parameter establishes the permissions of the views that must
            be accessible without logging in.
            Basically replace ``AllowAny`` with the specified class.
            """)
    ),
]

SETTINGS_FIELDS_GROUPS_MAP = OrderedDict([
    ('user', USER_SETTINGS_FIELDS),
    ('register', REGISTER_SETTINGS_FIELDS),
    ('login', LOGIN_SETTINGS_FIELDS),
    ('reset_password', RESET_PASSWORD_SETTINGS_FIELDS),
    ('register_email', REGISTER_EMAIL_SETTINGS_FIELDS),
    ('global_verification', GLOBAL_VERIFICATION_SETTINGS_FIELDS),
    ('change_password', CHANGE_PASSWORD_SETTINGS_FIELDS),
    ('profile', PROFILE_SETTINGS_FIELDS),
    ('misc', MISC_SETTINGS_FIELDS),
    ('permissons', PERMISSIONS_SETTINGS_FIELDS),
])

SETTINGS_FIELDS_GROUPS = list(SETTINGS_FIELDS_GROUPS_MAP.values())

SETTINGS_FIELDS = [f for fields in SETTINGS_FIELDS_GROUPS for f in fields]
