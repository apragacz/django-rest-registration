from collections import namedtuple
from typing import Any, Callable, Dict

from django.core.exceptions import ImproperlyConfigured
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils.translation import gettext as _

from rest_registration.settings import registration_settings
from rest_registration.utils.common import identity

EmailTemplateConfig = namedtuple('EmailTemplateConfig', (
    'subject_template_name',
    'text_body_template_name',
    'html_body_template_name',
    'text_body_processor',
))


def get_html_to_text_converter() -> Callable[[str], str]:
    return registration_settings.VERIFICATION_EMAIL_HTML_TO_TEXT_CONVERTER  # noqa: E501


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
    convert_html_to_text = get_html_to_text_converter()

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
