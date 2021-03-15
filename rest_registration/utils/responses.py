from typing import Any, Dict, Optional

from rest_framework.response import Response

from rest_registration.settings import registration_settings


def get_ok_response(
        message: str,
        status: int = 200,
        extra_data: Optional[Dict[str, Any]] = None) -> Response:
    builder = registration_settings.SUCCESS_RESPONSE_BUILDER
    response = builder(
        message=message, status=status, extra_data=extra_data)  # type: Response
    return response


def build_default_success_response(
        message: str,
        status: int,
        extra_data: Optional[Dict[str, Any]]) -> Response:
    data = {'detail': message}
    if extra_data:
        data.update(extra_data)
    return Response(data, status=status)
