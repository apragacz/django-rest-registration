import operator


def equals(first, second):
    return _print_operator_test(
        first, second, operator.eq, '{first!r}\n  should equal to\n{second!r}')


def _print_operator_test(first, second, op, fail_message_fmt):  # noqa: E501 pylint: disable=invalid-name
    if op(first, second):
        print('OK')  # noqa: T201
    else:
        fail_msg = fail_message_fmt.format(
            first=first,
            second=second,
            operator=op)
        print('FAIL:\n{fail_msg}'.format(fail_msg=fail_msg))  # noqa: T201
