
from django.contrib.auth import get_user_model
from django_dynamic_fixture import G


def shallow_merge_dicts(dictionary, *other_dicts):
    result = {}
    result.update(dictionary)
    for other_dict in other_dicts:
        result.update(other_dict)
    return result


def create_test_user(**kwargs):
    user_model = get_user_model()
    password = kwargs.pop('password', None)
    user = G(user_model, **kwargs)
    if password is not None:
        user.set_password(password)
        user.save()
        user.password_in_plaintext = password
    return user


def assert_len_equals(collection, expected_len, msg=None):
    std_msg = "{collection} does not have length {expected_len}".format(
        collection=collection,
        expected_len=expected_len,
    )
    assert len(collection) == expected_len, format_assert_message(msg, std_msg)


def format_assert_message(msg, standard_msg="assertion failed"):
    if msg is None:
        return standard_msg
    return "{standard_msg} : {msg}".format(standard_msg=standard_msg, msg=msg)
