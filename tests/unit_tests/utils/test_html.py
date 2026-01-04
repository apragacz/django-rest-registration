from textwrap import dedent

import pytest

from rest_registration.utils.html import MLStripperParseFailed, convert_html_to_text


@pytest.mark.parametrize(
    ("html", "kwargs", "expected_text"),
    [
        pytest.param(
            dedent(
                """\
            <!DOCTYPE html>
            <html><body>
                Look &amp; click
                <a href="https://example.com">here</a>
            </body></html>"""
            ),
            {"preserve_urls": True},
            "Look & click here (https://example.com)",
            id="entityref and link",
        ),
        pytest.param(
            dedent(
                """\
            <!DOCTYPE html>
            <html><body>
                Look &amp; click
                <a href="https://example.com?timestamp=1234">here</a>
            </body></html>"""
            ),
            {"preserve_urls": True},
            "Look & click here (https://example.com?timestamp=1234)",
            id="entityref and link with query",
        ),
        pytest.param(
            dedent(
                """\
            <!DOCTYPE html>
            <html><body>
                Look &#38; click here
            </body></html>"""
            ),
            {"preserve_urls": True},
            "Look & click here",
            id="charref",
        ),
        pytest.param(
            dedent(
                """\
            <html><body>
                Look &#38; click here
            </body></html>"""
            ),
            {"preserve_urls": True},
            "Look & click here",
            id="missing doctype",
        ),
        pytest.param(
            dedent(
                """\
            <!DOCTYPE html>
            <html><body>
                Look &amp; click on
                <a href="https://example.com">https://example.com</a>
            </body></html>"""
            ),
            {"preserve_urls": True},
            "Look & click on https://example.com",
            id="entityref and url link",
        ),
        pytest.param(
            dedent(
                """\
            <!DOCTYPE html>
            <html><body>
                I'm here, <br> click
                <a href="https://example.com">me</a>
            </body></html>"""
            ),
            {"preserve_urls": True},
            "I'm here,\nclick me (https://example.com)",
            id="newline tag with link",
        ),
        pytest.param(
            dedent(
                """\
            <!DOCTYPE html>
            <html><body>
                I'm here, <br/> click
                <a href="https://example.com">me</a>
            </body></html>"""
            ),
            {"preserve_urls": True},
            "I'm here,\nclick me (https://example.com)",
            id="newline tag (slash) with link",
        ),
        pytest.param(
            dedent(
                """\
            <!DOCTYPE html>
            <html><body>
                I'm here, <br/> click
                <a href="https://example.com">me</a>
            </body></html>"""
            ),
            {"preserve_urls": False},
            "I'm here,\nclick me",
            id="paragraphs with link, no urls preserving",
        ),
        pytest.param(
            dedent(
                """\
            <!DOCTYPE html>
            <html><body>
                <p>I'm here!</p>
                <p>Click <a href="https://example.com">me</a></p>
            </body></html>"""
            ),
            {"preserve_urls": True},
            "I'm here!\nClick me (https://example.com)\n",
            id="paragraphs with link",
        ),
        pytest.param(
            dedent(
                """\
            <!DOCTYPE html>
            <html>
                <head>
                    <title>I'm here</title>
                </head>
                <body>
                    <p>I'm here!</p>
                    <p>Click <a href="https://example.com">me</a></p>
                </body>
            </html>"""
            ),
            {"preserve_urls": True},
            "I'm here!\nClick me (https://example.com)\n",
            id="html head",
        ),
        pytest.param(
            dedent(
                """\
            <!DOCTYPE html>
            <html><body>
                <p>&copy; by SomeCompany;</p>
                <p>SomeMark &reg; is registered trademark</p>
            </body></html>"""
            ),
            {"preserve_urls": True},
            "\u00A9 by SomeCompany;\nSomeMark \u00AE is registered trademark\n",
            id="entityref",
        ),
        pytest.param(
            dedent(
                """\
            <!DOCTYPE html>
            <html><body>
                <p>&#169; by SomeCompany;</p>
                <p>SomeMark &#174; is registered trademark</p>
            </body></html>"""
            ),
            {"preserve_urls": True},
            "\u00A9 by SomeCompany;\nSomeMark \u00AE is registered trademark\n",
            id="charref2",
        ),
    ],
)
def test_convert_html_to_text_succeeds(html, kwargs, expected_text):
    assert convert_html_to_text(html, **kwargs) == expected_text


@pytest.mark.parametrize(
    ("html", "kwargs"),
    [
        pytest.param(
            "<![spam]><html><body>eggs</body><html>",
            {"preserve_urls": True},
            id="invalid declaration",
        ),
    ],
)
def test_convert_html_to_text_fails(html, kwargs):
    with pytest.raises(MLStripperParseFailed, match=r"spam"):
        convert_html_to_text(html, **kwargs)
