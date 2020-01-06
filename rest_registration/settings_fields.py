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
            to customise validation logic. Please remember that it should
            implement ``get_email`` method.
            """),
    ),
    Field('REGISTER_EMAIL_VERIFICATION_ENABLED', default=True),
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
