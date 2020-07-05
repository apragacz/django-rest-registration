import pytest
from rest_framework.exceptions import ValidationError

from rest_registration.utils.validation import run_validators


def fake_validator_raising_with_text(value):
    raise ValidationError('Some message')


def fake_validator_raising_with_list(value):
    raise ValidationError(['Some message 1', 'Some message 2'])


def fake_validator_raising_with_dict(value):
    raise ValidationError({'field': ['Some message']})


def fake_validator_raising_with_dict2(value):
    raise ValidationError({'field2': ['Some message']})


@pytest.mark.parametrize('validators,expected_exc_detail', [
    pytest.param(
        [
            fake_validator_raising_with_text,
        ],
        ['Some message'],
        id='text',
    ),
    pytest.param(
        [
            fake_validator_raising_with_text,
            fake_validator_raising_with_list,
        ],
        ['Some message', 'Some message 1', 'Some message 2'],
        id='text and list',
    ),
    pytest.param(
        [
            fake_validator_raising_with_dict,
            fake_validator_raising_with_dict2,
        ],
        {
            'field': ['Some message'],
            'field2': ['Some message'],
            'non_field_errors': [],
        },
        id='dicts',
    ),
    pytest.param(
        [
            fake_validator_raising_with_text,
            fake_validator_raising_with_list,
            fake_validator_raising_with_dict,
            fake_validator_raising_with_dict2,
        ],
        {
            'field': ['Some message'],
            'field2': ['Some message'],
            'non_field_errors': [
                'Some message', 'Some message 1', 'Some message 2'],
        },
        id='mixed',
    ),
])
def test_run_validators_fails(validators, expected_exc_detail):
    value = {}
    with pytest.raises(ValidationError) as exc_info:
        run_validators(validators, value)

    assert exc_info.value.detail == expected_exc_detail
