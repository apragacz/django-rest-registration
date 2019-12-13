from urllib.parse import parse_qs, urlparse

import pytest


def assert_valid_verification_url(
        url, expected_path=None, expected_fields=None,
        url_parser=None):
    if url_parser is None:
        url_parser = _parse_verification_url
    try:
        url_path, verification_data = url_parser(url, expected_fields)
    except ValueError as exc:
        pytest.fail(str(exc))
    if expected_path is not None:
        assert url_path == expected_path
    if expected_fields is not None:
        assert set(verification_data.keys()) == set(expected_fields)
    return verification_data


def _parse_verification_url(url, verification_field_names):
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query, strict_parsing=True)

    for key, values in query.items():
        if not values:
            raise ValueError("no values for '{key}".format(key=key))
        if len(values) > 1:
            raise ValueError("multiple values for '{key}'".format(key=key))

    verification_data = {key: values[0] for key, values in query.items()}
    return parsed_url.path, verification_data
