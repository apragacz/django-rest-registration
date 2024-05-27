import pytest
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ErrorDetail, ValidationError

from rest_registration.utils.validation import (
    run_validators,
    transform_django_validation_error,
)


def fake_validator_raising_with_text(value):
    raise ValidationError("Some message")


def fake_validator_raising_with_list(value):
    raise ValidationError(["Some message 1", "Some message 2"])


def fake_validator_raising_with_dict(value):
    raise ValidationError({"field": ["Some message"]})


def fake_validator_raising_with_dict2(value):
    raise ValidationError({"field2": ["Some message"]})


@pytest.mark.parametrize(
    ("validators", "expected_exc_detail"),
    [
        pytest.param(
            [
                fake_validator_raising_with_text,
            ],
            ["Some message"],
            id="text",
        ),
        pytest.param(
            [
                fake_validator_raising_with_text,
                fake_validator_raising_with_list,
            ],
            ["Some message", "Some message 1", "Some message 2"],
            id="text and list",
        ),
        pytest.param(
            [
                fake_validator_raising_with_dict,
                fake_validator_raising_with_dict2,
            ],
            {
                "field": ["Some message"],
                "field2": ["Some message"],
                "non_field_errors": [],
            },
            id="dicts",
        ),
        pytest.param(
            [
                fake_validator_raising_with_text,
                fake_validator_raising_with_list,
                fake_validator_raising_with_dict,
                fake_validator_raising_with_dict2,
            ],
            {
                "field": ["Some message"],
                "field2": ["Some message"],
                "non_field_errors": [
                    "Some message",
                    "Some message 1",
                    "Some message 2",
                ],
            },
            id="mixed",
        ),
    ],
)
def test_run_validators_fails(validators, expected_exc_detail):
    value = {}
    with pytest.raises(ValidationError) as exc_info:
        run_validators(validators, value)

    assert exc_info.value.detail == expected_exc_detail


@pytest.mark.parametrize(
    ("input_exc", "expected_output_exc"),
    [
        pytest.param(
            DjangoValidationError("error msg", code="errcode-1"),
            ValidationError([ErrorDetail("error msg", code="errcode-1")]),
            id="simple",
        ),
        pytest.param(
            DjangoValidationError(
                [
                    DjangoValidationError("error msg foo", code="errcode-1"),
                    DjangoValidationError("error msg bar", code="errcode-2"),
                ]
            ),
            ValidationError(
                [
                    ErrorDetail("error msg foo", code="errcode-1"),
                    ErrorDetail("error msg bar", code="errcode-2"),
                ]
            ),
            id="list",
        ),
        pytest.param(
            DjangoValidationError(
                {
                    "f1": [
                        DjangoValidationError("error msg foo", code="errcode-1"),
                        DjangoValidationError("error msg bar", code="errcode-2"),
                    ],
                    "f2": [
                        DjangoValidationError("error msg foobar", code="errcode-3"),
                    ],
                }
            ),
            ValidationError(
                {
                    "f1": [
                        ErrorDetail("error msg foo", code="errcode-1"),
                        ErrorDetail("error msg bar", code="errcode-2"),
                    ],
                    "f2": [
                        ErrorDetail("error msg foobar", code="errcode-3"),
                    ],
                }
            ),
            id="dict",
        ),
    ],
)
def test_transform_django_validation_error(input_exc, expected_output_exc):
    output_exc = transform_django_validation_error(input_exc)
    assert isinstance(output_exc, ValidationError)
    assert output_exc.args[0] == expected_output_exc.args[0]
