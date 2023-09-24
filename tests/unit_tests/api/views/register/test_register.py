from urllib.parse import quote_plus as urlquote
from urllib.parse import unquote_plus as urlunquote
from urllib.parse import urlparse

import pytest
from django.contrib.auth import get_user_model
from django.core.mail.backends.base import BaseEmailBackend
from django.test.utils import override_settings

from rest_registration.signers.register import RegisterSigner
from tests.helpers.api_views import (
    assert_response_status_is_bad_request,
    assert_response_status_is_created,
    assert_response_status_is_not_found
)
from tests.helpers.common import create_test_user
from tests.helpers.constants import REGISTER_VERIFICATION_URL, VERIFICATION_FROM_EMAIL
from tests.helpers.email import (
    assert_no_email_sent,
    assert_one_email_sent,
    capture_sent_emails
)
from tests.helpers.settings import override_rest_registration_settings
from tests.helpers.text import (
    assert_one_url_in_brackets_in_text,
    assert_one_url_line_in_text
)
from tests.helpers.timer import capture_time
from tests.helpers.verification import assert_valid_verification_url
from tests.helpers.views import ViewProvider
from tests.testapps.custom_users.models import UserType


def build_custom_verification_url(signer):
    base_url = signer.get_base_url()
    signed_data = signer.get_signed_data()
    if signer.USE_TIMESTAMP:
        timestamp = signed_data.pop(signer.TIMESTAMP_FIELD)
    else:
        timestamp = None
    signature = signed_data.pop(signer.SIGNATURE_FIELD)
    segments = [signed_data[k] for k in sorted(signed_data.keys())]
    segments.append(signature)
    if timestamp:
        segments.append(timestamp)
    quoted_segments = [urlquote(str(s)) for s in segments]

    url = base_url
    if not url.endswith('/'):
        url += '/'
    url += '/'.join(quoted_segments)
    url += '/'
    if signer.request:
        url = signer.request.build_absolute_uri(url)

    return url


def parse_custom_verification_url(url, verification_field_names):
    parsed_url = urlparse(url)
    num_of_fields = len(verification_field_names)
    url_path = parsed_url.path.rstrip('/')
    url_segments = url_path.rsplit('/', num_of_fields)
    if len(url_segments) != num_of_fields + 1:
        raise ValueError("Could not parse {url}".format(url=url))

    data_segments = url_segments[1:]
    url_path = url_segments[0] + '/'
    verification_data = {
        name: urlunquote(value)
        for name, value in zip(verification_field_names, data_segments)}
    return url_path, verification_data


@pytest.mark.django_db
def test_ok(
    settings_with_register_verification,
    api_view_provider, api_factory,
):
    data = _get_register_user_data(password='testpassword')
    request = api_factory.create_post_request(data)
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_status_is_created(response)
    # Check database state.
    user = _get_register_response_user(response)
    assert_user_state_matches_data(user, data)
    # Check verification e-mail.
    assert_one_email_sent(sent_emails)
    sent_email = sent_emails[0]
    assert_valid_register_verification_email(sent_email, user, timer)


@pytest.mark.django_db
@override_rest_registration_settings({
    'REGISTER_SERIALIZER_CLASS': 'tests.testapps.custom_users.serializers.RegisterUserSerializer',  # noqa: E501
})
def test_ok_with_user_with_relations(
    settings_with_register_verification,
    settings_with_user_with_channel,
    api_view_provider, api_factory,
):
    data = _get_register_user_data(password='testpassword')
    data["primary_channel"] = {
        "name": "fake-channel",
        "description": "blah",
    }
    request = api_factory.create_post_request(data, format="json")
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_status_is_created(response)
    # Check database state.
    user = _get_register_response_user(response)
    assert_user_state_matches_data(user, data)
    # Check verification e-mail.
    assert_one_email_sent(sent_emails)
    sent_email = sent_emails[0]
    assert_valid_register_verification_email(sent_email, user, timer)


@pytest.mark.django_db
@override_rest_registration_settings({
    'USER_VERIFICATION_ID_FIELD': 'username',
})
def test_ok_with_username_as_verification_id(
    settings_with_register_verification,
    api_view_provider, api_factory,
):
    # Using username is not recommended if it can change for a given user.
    data = _get_register_user_data(password='testpassword')
    request = api_factory.create_post_request(data)
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_status_is_created(response)
    # Check database state.
    user = _get_register_response_user(response)
    assert_user_state_matches_data(user, data)
    # Check verification e-mail.
    assert_one_email_sent(sent_emails)
    sent_email = sent_emails[0]
    assert_valid_sent_email_headers(sent_email, user)
    url = assert_one_url_line_in_text(sent_email.body)

    verification_data = assert_valid_verification_url(
        url,
        expected_path=REGISTER_VERIFICATION_URL,
        expected_fields={'signature', 'user_id', 'timestamp'},
    )
    url_username = verification_data['user_id']
    assert url_username == user.username
    assert_valid_register_verification_data_time(verification_data, timer)
    assert_register_verification_data_signer_verifies(verification_data)


@pytest.mark.django_db
@override_rest_registration_settings({
    'VERIFICATION_URL_BUILDER': build_custom_verification_url,
})
def test_ok_with_custom_verification_url(
    settings_with_register_verification,
    api_view_provider, api_factory,
):
    data = _get_register_user_data(password='testpassword')
    request = api_factory.create_post_request(data)
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_status_is_created(response)
    # Check database state.
    user = _get_register_response_user(response)
    assert_user_state_matches_data(user, data)
    # Check verification e-mail.
    assert_one_email_sent(sent_emails)
    sent_email = sent_emails[0]
    assert_valid_sent_email_headers(sent_email, user)
    url = assert_one_url_line_in_text(sent_email.body)

    verification_data = assert_valid_verification_url(
        url,
        expected_path=REGISTER_VERIFICATION_URL,
        expected_fields=['user_id', 'signature', 'timestamp'],
        url_parser=parse_custom_verification_url,
    )
    assert_valid_register_verification_data_user_id(verification_data, user)
    assert_valid_register_verification_data_time(verification_data, timer)
    assert_register_verification_data_signer_verifies(verification_data)


@pytest.mark.django_db
@override_rest_registration_settings({
    'REGISTER_VERIFICATION_EMAIL_TEMPLATES': {
        'subject': 'rest_registration/register/subject.txt',
        'html_body': 'rest_registration/register/body.html',
    },
})
def test_ok_with_html_email(
    settings_with_register_verification,
    api_view_provider, api_factory,
):
    data = _get_register_user_data(password='testpassword')
    request = api_factory.create_post_request(data)
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_status_is_created(response)
    # Check database state.
    user = _get_register_response_user(response)
    assert_user_state_matches_data(user, data)
    # Check verification e-mail.
    assert_one_email_sent(sent_emails)
    sent_email = sent_emails[0]
    assert_valid_sent_email_headers(sent_email, user)
    url = assert_one_url_in_brackets_in_text(sent_email.body)

    verification_data = assert_valid_verification_url(
        url,
        expected_path=REGISTER_VERIFICATION_URL,
        expected_fields={'signature', 'user_id', 'timestamp'},
    )
    assert_valid_register_verification_data_user_id(verification_data, user)
    assert_valid_register_verification_data_time(verification_data, timer)
    assert_register_verification_data_signer_verifies(verification_data)


@pytest.mark.django_db
@override_rest_registration_settings({
    'REGISTER_SERIALIZER_PASSWORD_CONFIRM': False,
})
def test_ok_when_no_password_confirm(
    settings_with_register_verification,
    api_view_provider, api_factory,
):
    data = _get_register_user_data(password='testpassword')
    data.pop('password_confirm')
    request = api_factory.create_post_request(data)
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_status_is_created(response)
    # Check database state.
    user = _get_register_response_user(response)
    assert_user_state_matches_data(user, data)
    # Check verification e-mail.
    assert_one_email_sent(sent_emails)
    sent_email = sent_emails[0]
    assert_valid_register_verification_email(sent_email, user, timer)


@pytest.mark.django_db
def test_ok_when_same_username(
    settings_with_register_verification,
    api_view_provider, api_factory,
):
    create_test_user(username='testusername')

    data = _get_register_user_data(
        username='testusername',
        password='testpassword',
    )

    request = api_factory.create_post_request(data)
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_response_status_is_bad_request(response)
    assert_no_email_sent(sent_emails)


@pytest.mark.django_db
@override_rest_registration_settings({
    'REGISTER_VERIFICATION_ENABLED': False,
})
def test_ok_without_verification(
    settings_with_register_verification,
    api_view_provider, api_factory,
):
    data = _get_register_user_data(password='testpassword')
    request = api_factory.create_post_request(data)
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_response_status_is_created(response)
    user = _get_register_response_user(response)
    assert_user_state_matches_data(user, data, verified=True)
    assert_no_email_sent(sent_emails)


@pytest.mark.django_db
@override_settings(
    TEMPLATES=(),
)
@override_rest_registration_settings({
    'REGISTER_VERIFICATION_ENABLED': False,
})
def test_ok_without_templates_without_verification(
    settings_with_register_verification,
    api_view_provider, api_factory,
):
    data = _get_register_user_data(password='testpassword')
    request = api_factory.create_post_request(data)
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_response_status_is_created(response)
    user = _get_register_response_user(response)
    assert_user_state_matches_data(user, data, verified=True)
    assert_no_email_sent(sent_emails)


@pytest.mark.django_db
def test_fail_when_missing_email(
    settings_with_register_verification,
    api_view_provider, api_factory,
):
    data = _get_register_user_data(password='testpassword')
    del data['email']
    request = api_factory.create_post_request(data)
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_response_status_is_bad_request(response)
    assert_no_email_sent(sent_emails)


@pytest.mark.django_db
def test_fail_when_empty_email(
    settings_with_register_verification,
    api_view_provider, api_factory,
):
    data = _get_register_user_data(password='testpassword', email='')
    request = api_factory.create_post_request(data)
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_response_status_is_bad_request(response)
    assert_no_email_sent(sent_emails)


@pytest.mark.django_db
@override_rest_registration_settings(
    {'USE_NON_FIELD_ERRORS_KEY_FROM_DRF_SETTINGS': True}
)
def test_fail_when_empty_email_non_field_errors(
    settings_with_register_verification,
    api_view_provider, api_factory,
):
    data = _get_register_user_data(password='testpassword', email='')
    request = api_factory.create_post_request(data)
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_response_status_is_bad_request(response)
    assert_no_email_sent(sent_emails)
    assert "non_field_errors" in response.data


@pytest.mark.django_db
def test_fail_when_short_password(
    settings_with_register_verification,
    api_view_provider, api_factory,
):
    data = _get_register_user_data(password='a')
    request = api_factory.create_post_request(data)
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_response_status_is_bad_request(response)
    assert_no_email_sent(sent_emails)


@pytest.mark.django_db
def test_fail_when_password_numeric(
    settings_with_register_verification,
    api_view_provider, api_factory,
):
    data = _get_register_user_data(password='4321332211113322')
    request = api_factory.create_post_request(data)
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_response_status_is_bad_request(response)
    assert_no_email_sent(sent_emails)


@pytest.mark.django_db
def test_fail_when_password_same_as_username(
    settings_with_register_verification,
    api_view_provider, api_factory,
):
    username = 'testusername'
    data = _get_register_user_data(
        username=username,
        password=username,
    )
    request = api_factory.create_post_request(data)
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_response_status_is_bad_request(response)
    assert_no_email_sent(sent_emails)


@pytest.mark.django_db
def test_fail_when_not_matching_password(
    settings_with_register_verification,
    api_view_provider, api_factory,
):
    data = _get_register_user_data(
        password='testpassword1',
        password_confirm='testpassword2')
    request = api_factory.create_post_request(data)
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_response_status_is_bad_request(response)
    assert_no_email_sent(sent_emails)


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND='tests.unit_tests.api.views.register.test_register.FailureEmailBackend',  # noqa E501
)
def test_fail_when_notification_failure(
    settings_with_register_verification,
    api_view_provider, api_factory,
):
    user_class = get_user_model()
    data = _get_register_user_data(password='testpassword')
    request = api_factory.create_post_request(data)
    user_ids_before = {u.pk for u in user_class.objects.all()}
    with capture_sent_emails() as sent_emails, pytest.raises(ConnectionRefusedError):
        api_view_provider.view_func(request)
    assert_no_email_sent(sent_emails)
    user_ids_after = {u.pk for u in user_class.objects.all()}
    assert user_ids_after == user_ids_before


@pytest.mark.django_db
def test_ok_when_user_with_foreign_key(
        settings_with_register_verification,
        settings_with_user_with_user_type,
        api_view_provider, api_factory):
    data = _get_register_user_data(password='testpassword')
    user_type = UserType.objects.create(name='custorme')
    data['user_type'] = user_type.id
    request = api_factory.create_post_request(data)
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_status_is_created(response)
    user = _get_register_response_user(response)
    assert_user_state_matches_data(user, data)

    assert_one_email_sent(sent_emails)
    sent_email = sent_emails[0]
    assert_valid_register_verification_email(sent_email, user, timer)


@pytest.mark.django_db
@override_rest_registration_settings({
    'VERIFICATION_TEMPLATES_SELECTOR': 'tests.testapps.custom_templates.utils.select_verification_templates',  # noqa E501
})
def test_ok_when_custom_verification_template_selector(
        settings_with_register_verification,
        api_view_provider, api_factory):
    data = _get_register_user_data(password='testpassword')
    request = api_factory.create_post_request(data)
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_status_is_created(response)
    user = _get_register_response_user(response)
    assert_user_state_matches_data(user, data)

    assert_one_email_sent(sent_emails)
    sent_email = sent_emails[0]
    assert sent_email.subject == "Generic verification link was sent"
    assert sent_email.body.startswith("Click URL to verify:")
    assert_valid_register_verification_email(sent_email, user, timer)


@pytest.mark.django_db
@override_rest_registration_settings({
    'VERIFICATION_TEMPLATES_SELECTOR': 'tests.testapps.custom_templates.utils.faulty_select_verification_templates',  # noqa E501
})
def test_ok_when_faulty_verification_template_selector(
        settings_with_register_verification,
        api_view_provider, api_factory):
    data = _get_register_user_data(password='testpassword')
    request = api_factory.create_post_request(data)
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_status_is_created(response)
    user = _get_register_response_user(response)
    assert_user_state_matches_data(user, data)

    assert_one_email_sent(sent_emails)
    sent_email = sent_emails[0]
    assert_valid_register_verification_email(sent_email, user, timer)


@pytest.mark.django_db
@override_rest_registration_settings({
    'REGISTER_FLOW_ENABLED': False,
})
def test_fail_when_register_flow_disabled(
        settings_with_register_verification,
        api_view_provider, api_factory):
    data = _get_register_user_data(password='testpassword')
    request = api_factory.create_post_request(data)
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_response_status_is_not_found(response)
    assert_no_email_sent(sent_emails)


@pytest.fixture()
def api_view_provider():
    return ViewProvider('register')


def assert_user_state_matches_data(user, data, verified=False):
    assert user.username == data['username']
    assert user.email == data['email']
    assert user.check_password(data['password'])
    assert user.is_active == verified


def assert_valid_register_verification_email(sent_email, user, timer):
    assert_valid_sent_email_headers(sent_email, user)
    url = assert_one_url_line_in_text(sent_email.body)

    verification_data = assert_valid_verification_url(
        url,
        expected_path=REGISTER_VERIFICATION_URL,
        expected_fields={'signature', 'user_id', 'timestamp'},
    )
    assert_valid_register_verification_data_user_id(verification_data, user)
    assert_valid_register_verification_data_time(verification_data, timer)
    assert_register_verification_data_signer_verifies(verification_data)


def assert_valid_sent_email_headers(sent_email, user):
    assert sent_email.from_email == VERIFICATION_FROM_EMAIL
    assert sent_email.to == [user.email]


def assert_valid_register_verification_data_user_id(verification_data, user):
    url_user_id = int(verification_data['user_id'])
    assert url_user_id == user.pk


def assert_valid_register_verification_data_time(verification_data, timer):
    url_sig_timestamp = int(verification_data['timestamp'])
    assert timer.start_time <= url_sig_timestamp <= timer.end_time


def assert_register_verification_data_signer_verifies(verification_data):
    signer = RegisterSigner(verification_data)
    signer.verify()


def _get_register_response_user(response):
    user_id = response.data['id']
    user_class = get_user_model()
    user = user_class.objects.get(id=user_id)
    return user


def _get_register_user_data(password, password_confirm=None, **options):
    username = 'testusername'
    email = 'testusername@example.com'
    if password_confirm is None:
        password_confirm = password
    data = {
        'username': username,
        'password': password,
        'password_confirm': password_confirm,
        'email': email,
    }
    data.update(options)
    return data


class FailureEmailBackend(BaseEmailBackend):

    def send_messages(self, email_messages):
        if not email_messages:
            return
        raise ConnectionRefusedError()
