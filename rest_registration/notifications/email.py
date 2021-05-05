from collections import namedtuple
from typing import TYPE_CHECKING, Any, Dict

from django.core.exceptions import ImproperlyConfigured
from django.core.mail.message import EmailMultiAlternatives
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template, render_to_string
from django.utils.translation import gettext as _

from rest_registration.notifications.enums import NotificationMethod, NotificationType
from rest_registration.settings import registration_settings
from rest_registration.utils.common import identity
from rest_registration.utils.users import get_user_email_field_name

if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser

EmailTemplateConfig = namedtuple('EmailTemplateConfig', (
    'subject_template_name',
    'text_body_template_name',
    'html_body_template_name',
    'text_body_processor',
))


def send_verification_notification(
        notification_type: NotificationType,
        user: 'AbstractBaseUser',
        data: Dict[str, Any],
        template_config_data: Dict[str, Any],
        custom_user_address: Any = None) -> None:
    if custom_user_address is None:
        user_address = get_user_address(user)
    else:
        user_address = custom_user_address
    notification = create_verification_notification(
        notification_type, user, user_address, data, template_config_data)
    send_notification(notification)


def create_verification_notification(
        notification_type: NotificationType,
        user: 'AbstractBaseUser',
        user_address: Any,
        data: Dict[str, Any],
        template_config_data: Dict[str, Any]) -> EmailMultiAlternatives:
    from_email = registration_settings.VERIFICATION_FROM_EMAIL
    reply_to_email = (registration_settings.VERIFICATION_REPLY_TO_EMAIL or
                      from_email)
    template_context_builder = registration_settings.VERIFICATION_TEMPLATE_CONTEXT_BUILDER  # noqa: E501
    context = template_context_builder(
        user, user_address, data,
        notification_type=notification_type,
        notification_method=NotificationMethod.EMAIL)
    template_config = parse_template_config(template_config_data)

    subject = render_to_string(
        template_config.subject_template_name, context=context).strip()
    text_body = template_config.text_body_processor(
        render_to_string(
            template_config.text_body_template_name, context=context))

    email_msg = EmailMultiAlternatives(
        subject, text_body, from_email, [user_address],
        reply_to=[reply_to_email])

    if template_config.html_body_template_name:
        html_body = render_to_string(
            template_config.html_body_template_name, context=context)
        email_msg.attach_alternative(html_body, 'text/html')

    return email_msg


def send_notification(notification: EmailMultiAlternatives) -> None:
    notification.send()


def get_user_address(user: 'AbstractBaseUser') -> str:
    email_field_name = get_user_email_field_name()
    email = getattr(user, email_field_name)  # type: str
    return email


def parse_template_config(template_config_data: Dict[str, Any]) -> EmailTemplateConfig:
    """
    >>> from tests import doctest_utils
    >>> convert_html_to_text = registration_settings.VERIFICATION_EMAIL_HTML_TO_TEXT_CONVERTER  # noqa: E501
    >>> parse_template_config({})  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ImproperlyConfigured
    >>> parse_template_config({
    ...     'subject': 'blah',
    ... })  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ImproperlyConfigured
    >>> parse_template_config({
    ...     'subject': 'blah',
    ...     'body': 'blah',
    ... })  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ImproperlyConfigured
    >>> doctest_utils.equals(
    ...     parse_template_config({
    ...         'subject': 'rest_registration/register/subject.txt',
    ...         'html_body': 'rest_registration/register/body.html',
    ...         'text_body': 'rest_registration/register/body.txt',
    ...     }),
    ...     EmailTemplateConfig(
    ...         'rest_registration/register/subject.txt',
    ...         'rest_registration/register/body.txt',
    ...         'rest_registration/register/body.html',
    ...         identity))
    OK
    >>> doctest_utils.equals(
    ...     parse_template_config({
    ...         'subject': 'rest_registration/register/subject.txt',
    ...         'html_body': 'rest_registration/register/body.html',
    ...     }),
    ...     EmailTemplateConfig(
    ...         'rest_registration/register/subject.txt',
    ...         'rest_registration/register/body.html',
    ...         'rest_registration/register/body.html',
    ...         convert_html_to_text))
    OK
    >>> doctest_utils.equals(
    ...     parse_template_config({
    ...         'subject': 'rest_registration/register/subject.txt',
    ...         'text_body': 'rest_registration/register/body.txt',
    ...     }),
    ...     EmailTemplateConfig(
    ...         'rest_registration/register/subject.txt',
    ...         'rest_registration/register/body.txt', None,
    ...         identity))
    OK
    >>> doctest_utils.equals(
    ...     parse_template_config({
    ...         'subject': 'rest_registration/register/subject.txt',
    ...         'body': 'rest_registration/register/body.txt',
    ...     }),
    ...     EmailTemplateConfig(
    ...         'rest_registration/register/subject.txt',
    ...         'rest_registration/register/body.txt', None,
    ...         identity))
    OK
    >>> doctest_utils.equals(
    ...     parse_template_config({
    ...         'subject': 'rest_registration/register/subject.txt',
    ...         'body': 'rest_registration/register/body.html',
    ...         'is_html': True,
    ...     }),
    ...     EmailTemplateConfig(
    ...         'rest_registration/register/subject.txt',
    ...         'rest_registration/register/body.html',
    ...         'rest_registration/register/body.html',
    ...         convert_html_to_text))
    OK
    """
    try:
        subject_template_name = template_config_data['subject']
    except KeyError:
        raise ImproperlyConfigured(_("No 'subject' key found")) from None
    body_template_name = template_config_data.get('body')
    text_body_template_name = template_config_data.get('text_body')
    html_body_template_name = template_config_data.get('html_body')
    is_html_body = template_config_data.get('is_html')
    convert_html_to_text = registration_settings.VERIFICATION_EMAIL_HTML_TO_TEXT_CONVERTER  # noqa: E501

    if html_body_template_name and text_body_template_name:
        config = EmailTemplateConfig(
            subject_template_name=subject_template_name,
            text_body_template_name=text_body_template_name,
            html_body_template_name=html_body_template_name,
            text_body_processor=identity,
        )
    elif html_body_template_name:
        config = EmailTemplateConfig(
            subject_template_name=subject_template_name,
            text_body_template_name=html_body_template_name,
            html_body_template_name=html_body_template_name,
            text_body_processor=convert_html_to_text,
        )
    elif text_body_template_name:
        config = EmailTemplateConfig(
            subject_template_name=subject_template_name,
            text_body_template_name=text_body_template_name,
            html_body_template_name=None,
            text_body_processor=identity,
        )
    elif body_template_name:
        if is_html_body:
            config = EmailTemplateConfig(
                subject_template_name=subject_template_name,
                text_body_template_name=body_template_name,
                html_body_template_name=body_template_name,
                text_body_processor=convert_html_to_text,
            )
        else:
            config = EmailTemplateConfig(
                subject_template_name=subject_template_name,
                text_body_template_name=body_template_name,
                html_body_template_name=None,
                text_body_processor=identity,
            )
    else:
        raise ImproperlyConfigured(
            'Could not parse template config data: {template_config_data}'.format(  # noqa: E501
                template_config_data=template_config_data))

    _validate_template_name_existence(config.subject_template_name)
    _validate_template_name_existence(config.text_body_template_name)

    if config.html_body_template_name:
        _validate_template_name_existence(config.html_body_template_name)

    assert callable(config.text_body_processor)

    return config


def _validate_template_name_existence(template_name: str) -> None:
    try:
        get_template(template_name)
    except TemplateDoesNotExist:
        raise ImproperlyConfigured(
            'Template {template_name!r} does not exist; ensure that your'
            ' Django TEMPLATES setting is configured correctly'.format(
                template_name=template_name)) from None
