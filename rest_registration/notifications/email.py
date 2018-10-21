from collections import namedtuple

from django.core.exceptions import ImproperlyConfigured
from django.core.mail.message import EmailMultiAlternatives
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template, render_to_string

from rest_registration.settings import registration_settings
from rest_registration.utils.common import identity
from rest_registration.utils.users import get_user_setting

EmailTemplateConfig = namedtuple('EmailTemplateConfig', (
    'subject_template_name',
    'text_body_template_name',
    'html_body_template_name',
    'text_body_processor',
))


def send_verification_notification(
        user, params_signer, template_config_data, email=None):
    notification = create_verification_notification(
        user, params_signer, template_config_data, email=email)
    send_notification(notification)


def create_verification_notification(
        user, params_signer, template_config_data, email=None):
    if email is None:
        email_field = get_user_setting('EMAIL_FIELD')
        email = getattr(user, email_field)

    from_email = registration_settings.VERIFICATION_FROM_EMAIL
    reply_to_email = (registration_settings.VERIFICATION_REPLY_TO_EMAIL or
                      from_email)
    context = {
        'user': user,
        'email': email,
        'verification_url':  params_signer.get_url(),
    }
    template_config = parse_template_config(template_config_data)

    subject = render_to_string(
        template_config.subject_template_name, context=context).strip()
    text_body = template_config.text_body_processor(
        render_to_string(
            template_config.text_body_template_name, context=context))

    email_msg = EmailMultiAlternatives(
        subject, text_body, from_email, [email], reply_to=[reply_to_email])

    if template_config.html_body_template_name:
        html_body = render_to_string(
            template_config.html_body_template_name, context=context)
        email_msg.attach_alternative(html_body, 'text/html')

    return email_msg


def parse_template_config(template_config_data):
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
        raise ImproperlyConfigured("No 'subject' key found")
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


def _validate_template_name_existence(template_name):
    try:
        get_template(template_name)
    except TemplateDoesNotExist:
        raise ImproperlyConfigured(
            'Template {template_name!r} does not exists'.format(
                template_name=template_name))


def send_notification(notification):
    notification.send()
