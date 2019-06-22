from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods

from rest_registration.api.views.register import (
    process_verify_registration_data,
    signal_verify_registration
)
from rest_registration.api.views.register_email import (
    process_verify_email_data,
    signal_verify_email
)
from rest_registration.api.views.reset_password import (
    process_reset_password_data,
    signal_reset_password
)
from rest_registration.contrib.verification_redirects.settings import \
    verification_redirects_settings as vr_settings


@require_http_methods(['GET'])
def verify_registration(request):
    return _generic_redirect_view(
        request, process_verify_registration_data, signal_verify_registration,
        ['user_id', 'signature', 'timestamp'],
        vr_settings.VERIFY_REGISTRATION_SUCCESS_URL,
        vr_settings.VERIFY_REGISTRATION_FAILURE_URL)


@require_http_methods(['GET'])
def verify_email(request):
    return _generic_redirect_view(
        request, process_verify_email_data, signal_verify_email,
        ['user_id', 'email', 'signature', 'timestamp'],
        vr_settings.VERIFY_EMAIL_SUCCESS_URL,
        vr_settings.VERIFY_EMAIL_FAILURE_URL)


@require_http_methods(['POST'])
def reset_password(request):
    return _generic_redirect_view(
        request, process_reset_password_data, signal_reset_password,
        ['user_id', 'signature', 'timestamp', 'password'],
        vr_settings.RESET_PASSWORD_SUCCESS_URL,
        vr_settings.RESET_PASSWORD_FAILURE_URL,
        use_post_method=True)


def _generic_redirect_view(
        request, data_processor, signal_sender, data_keys,
        success_url, failure_url,
        use_post_method=False):
    query_dict = request.POST if use_post_method else request.GET
    data = {}
    for key in data_keys:
        data[key] = query_dict.get(key)
    try:
        processor_result = data_processor(data)
        signal_sender(request, processor_result)
        return redirect(success_url)
    except Exception:
        return redirect(failure_url)
