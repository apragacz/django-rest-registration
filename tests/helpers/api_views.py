
import rest_framework
from django.contrib.sessions.middleware import SessionMiddleware
from rest_framework import status
from rest_framework.test import APIRequestFactory

from .views import ViewProvider

rest_framework_version_info = tuple(
    int(s) for s in rest_framework.__version__.split('.'))


class APIViewRequestFactory:

    def __init__(self, view_provider: ViewProvider):
        self._factory = APIRequestFactory()
        self._view_provider = view_provider

    @property
    def view_url(self):
        return self._view_provider.view_url

    def create_post_request(self, data=None):
        return self._factory.post(self.view_url, data)

    def create_patch_request(self, data=None):
        return self._factory.patch(self.view_url, data)

    def create_get_request(self):
        return self._factory.get(self.view_url)

    def add_session_to_request(self, request):
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()


def assert_valid_response(response, expected_status_code=None):
    _assert_response(
        response,
        expected_valid_response=True,
        expected_status_code=expected_status_code)


def assert_invalid_response(response, expected_status_code=None):
    _assert_response(
        response,
        expected_valid_response=False,
        expected_status_code=expected_status_code)


def assert_response_is_ok(response):
    assert_valid_response(
        response,
        expected_status_code=status.HTTP_200_OK,
    )


def assert_response_is_bad_request(response):
    assert_invalid_response(
        response,
        expected_status_code=status.HTTP_400_BAD_REQUEST,
    )


def assert_response_is_not_found(response):
    assert_invalid_response(
        response,
        expected_status_code=status.HTTP_404_NOT_FOUND,
    )


def _assert_response(
        response, expected_valid_response=True,
        expected_status_code=None):
    status_code = response.status_code
    msg_format = "Response returned with code {status_code}, body {response.data}"  # noqa: E501
    msg = msg_format.format(
        status_code=status_code,
        response=response,
    )
    if expected_status_code is not None:
        assert status_code == expected_status_code, msg
    elif expected_valid_response:
        assert 200 <= status_code < 400, msg
    else:
        assert status_code < 200 or status_code >= 400, msg
