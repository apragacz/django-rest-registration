import re


def assert_no_url_in_text(text):
    _assert_urls_in_text(text, 0, r'https?://.*')


def assert_one_url_line_in_text(text):
    url_lines = _assert_urls_in_text(text, 1, r'^(?P<url>https?://.*)$')
    return url_lines[0]


def assert_one_url_in_brackets_in_text(text):
    urls = _assert_urls_in_text(text, 1, r'\((?P<url>https?://.*)\)')
    return urls[0]


def _assert_urls_in_text(text, expected_num, line_url_pattern):
    lines = [line.rstrip() for line in text.split('\n')]
    urls = []
    for line in lines:
        for match in re.finditer(line_url_pattern, line):
            match_groupdict = match.groupdict()
            urls.append(match_groupdict['url'])
    num_of_urls = len(urls)
    msg = f"Found {num_of_urls} urls instead of {expected_num} in:\n{text}"
    assert num_of_urls == expected_num, msg
    return urls
