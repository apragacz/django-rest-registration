import pytest

from rest_registration.utils.users import get_user_field_names


@pytest.mark.parametrize('kwargs,expected_fields', [
    (
        {},
        {'id', 'first_name', 'last_name', 'username', 'email'},
    ),
    (
        {'allow_primary_key': False},
        {'first_name', 'last_name', 'username', 'email'},
    ),
    (
        {'non_editable': True},
        {'id'},
    ),
    (
        {'allow_primary_key': False, 'non_editable': True},
        set(),
    ),
])
def test_get_user_field_names(kwargs, expected_fields):
    assert set(get_user_field_names(**kwargs)) == expected_fields
