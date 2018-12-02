import datetime
from collections import namedtuple

_Field = namedtuple('_Field', [
    'name',
    'default',
    'help',
    'import_string',
])


class Field(_Field):

    def __new__(cls, name, *, default=None, help=None, import_string=False):
        return super().__new__(
            cls, name=name, default=default,
            help=help, import_string=import_string)


USER_SETTINGS_FIELDS = [
    Field('USER_LOGIN_FIELDS'),
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
    Field('USER_PUBLIC_FIELDS'),
    Field('USER_EDITABLE_FIELDS'),
    Field('USER_EMAIL_FIELD', default='email'),
    Field('USER_VERIFICATION_FLAG_FIELD', default='is_active'),
]

REGISTER_SETTINGS_FIELDS = [
    Field(
        'REGISTER_SERIALIZER_CLASS',
        default='rest_registration.api.serializers.DefaultRegisterUserSerializer',  # noqa: E501,
        import_string=True,
    ),
    Field('REGISTER_SERIALIZER_PASSWORD_CONFIRM', default=True),

    Field(
        'REGISTER_OUTPUT_SERIALIZER_CLASS',
        default='rest_registration.api.serializers.DefaultUserProfileSerializer',  # noqa: E501,
        import_string=True,
    ),

    Field('REGISTER_VERIFICATION_ENABLED', default=True),
    Field('REGISTER_VERIFICATION_PERIOD', default=datetime.timedelta(days=7)),
    Field('REGISTER_VERIFICATION_URL'),
    Field(
        'REGISTER_VERIFICATION_EMAIL_TEMPLATES',
        default={
            'subject': 'rest_registration/register/subject.txt',
            'body': 'rest_registration/register/body.txt',
        },
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
]
RESET_PASSWORD_SETTINGS_FIELDS = [
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

SETTINGS_FIELDS_LIST = [
    USER_SETTINGS_FIELDS,
    REGISTER_SETTINGS_FIELDS,
    LOGIN_SETTINGS_FIELDS,
    RESET_PASSWORD_SETTINGS_FIELDS,
    REGISTER_EMAIL_SETTINGS_FIELDS,
    GLOBAL_VERIFICATION_SETTINGS_FIELDS,
    CHANGE_PASSWORD_SETTINGS_FIELDS,
    PROFILE_SETTINGS_FIELDS,
    MISC_SETTINGS_FIELDS,
]

SETTINGS_FIELDS = [f for fields in SETTINGS_FIELDS_LIST for f in fields]
