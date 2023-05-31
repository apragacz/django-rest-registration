import pytest
from django.core.exceptions import ImproperlyConfigured

from rest_registration.utils.common import identity
from rest_registration.utils.email import EmailTemplateConfig, parse_template_config
from rest_registration.utils.html import \
    convert_html_to_text_preserving_urls as default_convert_html_to_text


@pytest.mark.parametrize(
    "template_config_data,"
    "expected_result", [
        pytest.param(
            {
                'subject': 'rest_registration/register/subject.txt',
                'html_body': 'rest_registration/register/body.html',
                'text_body': 'rest_registration/register/body.txt',
            },
            EmailTemplateConfig(
                'rest_registration/register/subject.txt',
                'rest_registration/register/body.txt',
                'rest_registration/register/body.html',
                identity,
            ),
            id="both html and text body template",
        ),
        pytest.param(
            {
                'subject': 'rest_registration/register/subject.txt',
                'html_body': 'rest_registration/register/body.html',
            },
            EmailTemplateConfig(
                'rest_registration/register/subject.txt',
                'rest_registration/register/body.html',
                'rest_registration/register/body.html',
                default_convert_html_to_text,
            ),
            id="html body template only",
        ),
        pytest.param(
            {
                'subject': 'rest_registration/register/subject.txt',
                'text_body': 'rest_registration/register/body.txt',
            },
            EmailTemplateConfig(
                'rest_registration/register/subject.txt',
                'rest_registration/register/body.txt',
                None,
                identity,
            ),
            id="text body template only",
        ),
        pytest.param(
            {
                'subject': 'rest_registration/register/subject.txt',
                'body': 'rest_registration/register/body.txt',
            },
            EmailTemplateConfig(
                'rest_registration/register/subject.txt',
                'rest_registration/register/body.txt',
                None,
                identity,
            ),
            id="default text body template",
        ),
        pytest.param(
            {
                'subject': 'rest_registration/register/subject.txt',
                'body': 'rest_registration/register/body.html',
                'is_html': True,
            },
            EmailTemplateConfig(
                'rest_registration/register/subject.txt',
                'rest_registration/register/body.html',
                'rest_registration/register/body.html',
                default_convert_html_to_text,
            ),
            id="default html body template",
        ),
    ],
)
def test_parse_template_config_ok(template_config_data, expected_result):
    assert parse_template_config(template_config_data) == expected_result


@pytest.mark.parametrize(
    "template_config_data", [
        pytest.param(
            {},
            id="missing subject and body",
        ),
        pytest.param(
            {
                'subject': 'blah',
            },
            id="invalid subject, missing body",
        ),
        pytest.param(
            {
                'subject': 'blah',
                'body': 'blah',
            },
            id="invalid subject and body",
        ),
    ],
)
def test_parse_template_config_fail(template_config_data):
    with pytest.raises(ImproperlyConfigured):
        parse_template_config(template_config_data)
