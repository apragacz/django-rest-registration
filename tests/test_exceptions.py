import pytest

from rest_registration.exceptions import BadRequest, ErrorDetail
from tests.helpers.settings import override_rest_registration_settings


@pytest.mark.parametrize(
    "detail,"
    "code,"
    "expected_obj_detail", (
        ("test err", "test-err", ErrorDetail("test err", code="test-err")),
        (None, None, ErrorDetail("Bad Request", code="bad-request")),
    ),
)
def test_bad_request_detail(detail, code, expected_obj_detail):
    exc = BadRequest(detail=detail, code=code)
    assert exc.detail == expected_obj_detail


@pytest.mark.parametrize(
    "detail,"
    "expected_obj_detail", [
        pytest.param(
            None,
            {"non_field_errors": [ErrorDetail("Bad Request", code="bad-request")]},
            id="none",
        ),
        pytest.param(
            ["test err"],
            {"non_field_errors": [ErrorDetail("test err", code="bad-request")]},
            id="str_list",
        ),
        pytest.param(
            "test err",
            {"non_field_errors": [ErrorDetail("test err", code="bad-request")]},
            id="str",
        ),
        pytest.param(
            {"field": ["test err"]},
            {"field": [ErrorDetail("test err", code="bad-request")]},
            id="str_list_dict"
        ),
    ],
)
@override_rest_registration_settings({
    'USE_NON_FIELD_ERRORS_KEY_FROM_DRF_SETTINGS': True,
})
def test_bad_request_detail_with_use_non_field_errors_key(detail, expected_obj_detail):
    exc = BadRequest(detail=detail)
    assert exc.detail == expected_obj_detail
