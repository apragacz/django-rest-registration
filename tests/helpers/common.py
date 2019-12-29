
from django.contrib.auth import get_user_model


def shallow_merge_dicts(dictionary, *other_dicts):
    result = {}
    result.update(dictionary)
    for other_dict in other_dicts:
        result.update(other_dict)
    return result


def create_test_user(**kwargs):
    password = kwargs.pop('password', None)

    user_model = get_user_model()
    fields = user_model._meta.get_fields()  # pylint: disable=protected-access
    user_kwargs = {}

    for field in fields:
        name = field.name
        if name in USER_DEFAULT_FIELD_VALUES:
            user_kwargs[name] = USER_DEFAULT_FIELD_VALUES[name]
        else:
            assert field.null or field.default is not None

    user_kwargs.update(**kwargs)

    user = user_model.objects.create(**user_kwargs)
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


USER_DEFAULT_FIELD_VALUES = {
    'username': "john_doe",
    'first_name': "John",
    'last_name': "Doe",
    'full_name': "John Doe",
    'email': "john.doe@example.com",
}
