from typing import Callable, Dict, Iterable, Optional, Tuple, Type
from urllib.parse import parse_qs, urlparse

import pytest

from rest_registration.utils.signers import URLParamsSigner
from tests.helpers.timer import Timer


def assert_valid_verification_url(
        url: str,
        expected_path: Optional[str] = None,
        expected_fields: Iterable[str] = None,
        url_parser: Optional[Callable[
            [str, Optional[Iterable[str]]],
            Tuple[str, Dict[str, str]]]] = None,
        timer: Optional[Timer] = None,
        signer_cls: Optional[Type[URLParamsSigner]] = None,
):
    url_parser_ = url_parser if url_parser is not None else _parse_verification_url
    try:
        url_path, verification_data = url_parser_(url, expected_fields)
    except ValueError as exc:
        pytest.fail(str(exc))
    if expected_path is not None:
        assert url_path == expected_path
    if expected_fields is not None:
        assert set(verification_data.keys()) == set(expected_fields)

    if timer is not None:
        url_sig_timestamp = int(verification_data['timestamp'])
        assert timer.start_time <= url_sig_timestamp <= timer.end_time

    if signer_cls is not None:
        signer = signer_cls(verification_data)
        signer.verify()

    return verification_data


def _parse_verification_url(
        url: str,
        verification_field_names: Optional[Iterable[str]],
) -> Tuple[str, Dict[str, str]]:
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query, strict_parsing=True)

    for key, values in query.items():
        if not values:
            raise ValueError(f"no values for {key!r}")
        if len(values) > 1:
            raise ValueError(f"multiple values for {key!r}")

    verification_data = {key: values[0] for key, values in query.items()}
    return parsed_url.path, verification_data
