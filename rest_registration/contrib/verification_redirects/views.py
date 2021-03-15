from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from rest_framework.exceptions import APIException

from rest_registration.api.views.register import process_verify_registration_data
from rest_registration.api.views.register_email import process_verify_email_data
from rest_registration.api.views.reset_password import process_reset_password_data
from rest_registration.contrib.verification_redirects.settings import (
    verification_redirects_settings
)


@require_http_methods(['GET'])
def verify_registration(request):
    return _generic_redirect_view(
        request, process_verify_registration_data,
        ['user_id', 'signature', 'timestamp'],
        verification_redirects_settings.VERIFY_REGISTRATION_SUCCESS_URL,
        verification_redirects_settings.VERIFY_REGISTRATION_FAILURE_URL)


@require_http_methods(['GET'])
def verify_email(request):
    return _generic_redirect_view(
        request, process_verify_email_data,
        ['user_id', 'email', 'signature', 'timestamp'],
        verification_redirects_settings.VERIFY_EMAIL_SUCCESS_URL,
        verification_redirects_settings.VERIFY_EMAIL_FAILURE_URL)


@require_http_methods(['POST'])
def reset_password(request):
    return _generic_redirect_view(
        request, process_reset_password_data,
        ['user_id', 'signature', 'timestamp', 'password'],
        verification_redirects_settings.RESET_PASSWORD_SUCCESS_URL,
        verification_redirects_settings.RESET_PASSWORD_FAILURE_URL,
        use_post_method=True)


def _generic_redirect_view(
        request, data_processor, data_keys, success_url, failure_url,
        use_post_method=False):
    query_dict = request.POST if use_post_method else request.GET
    data = {}
    for key in data_keys:
        data[key] = query_dict.get(key)
    try:
        request = data_processor(data)
        return redirect(success_url)
    except APIException:
        return redirect(failure_url)
