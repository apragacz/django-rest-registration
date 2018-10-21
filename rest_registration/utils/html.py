from collections import deque, namedtuple
from html.entities import name2codepoint
from html.parser import HTMLParser


def convert_html_to_text_preserving_urls(value):
    return convert_html_to_text(value, preserve_urls=True)


def convert_html_to_text(value, preserve_urls=False):
    r"""
    >>> convert_html_to_text(
    ...     '''
    ...     <html><body>
    ...         Look &amp; click
    ...         <a href="https://example.com">here</a>
    ...     </body></html>''', preserve_urls=True)
    'Look & click here (https://example.com)'
    >>> convert_html_to_text(
    ...     '''
    ...     <html><body>
    ...         Look &amp; click
    ...         <a href="https://example.com?timestamp=1234">here</a>
    ...     </body></html>''', preserve_urls=True)
    'Look & click here (https://example.com?timestamp=1234)'
    >>> convert_html_to_text(
    ...     '''
    ...     <html><body>
    ...         Look &#38; click here
    ...     </body></html>''', preserve_urls=True)
    'Look & click here'
    >>> convert_html_to_text(
    ...     '''
    ...     <html><body>
    ...         Look &amp; click on
    ...         <a href="https://example.com">https://example.com</a>
    ...     </body></html>''', preserve_urls=True)
    'Look & click on https://example.com'
    >>> convert_html_to_text(
    ...     '''
    ...     <html><body>
    ...         I'm here, <br> click
    ...         <a href="https://example.com">me</a>
    ...     </body></html>''', preserve_urls=True)
    "I'm here,\nclick me (https://example.com)"
    >>> convert_html_to_text(
    ...     '''
    ...     <html><body>
    ...         I'm here, <br/> click
    ...         <a href="https://example.com">me</a>
    ...     </body></html>''', preserve_urls=True)
    "I'm here,\nclick me (https://example.com)"
    >>> convert_html_to_text(
    ...     '''
    ...     <html><body>
    ...         I'm here, <br/> click
    ...         <a href="https://example.com">me</a>
    ...     </body></html>''')
    "I'm here,\nclick me"
    >>> convert_html_to_text(
    ...     '''
    ...     <html><body>
    ...         <p>I'm here!</p>
    ...         <p>Click <a href="https://example.com">me</a></p>
    ...     </body></html>''', preserve_urls=True)
    "I'm here!\nClick me (https://example.com)\n"
    >>> convert_html_to_text(
    ...     '''
    ...     <html>
    ...         <head>
    ...             <title>I'm here</title>
    ...         </head>
    ...         <body>
    ...             <p>I'm here!</p>
    ...             <p>Click <a href="https://example.com">me</a></p>
    ...         </body>
    ...     </html>''', preserve_urls=True)
    "I'm here!\nClick me (https://example.com)\n"
    """
    s = MLStripper(preserve_urls=preserve_urls)
    s.feed(value)
    s.close()
    return s.get_data()


def _has_html_tags(value):
    return '<' in value and '>' in value


TagInfo = namedtuple('TagInfo', ('name', 'attrs'))


class MLStripper(HTMLParser):

    def __init__(self, preserve_urls=False):
        super(MLStripper, self).__init__()
        self.reset()
        self._paragraphs = [[]]
        self._tag_info_stack = deque([TagInfo(None, {})])
        self._preserve_urls = preserve_urls

    def handle_starttag(self, tag, attrs):
        self._tag_info_stack.append(TagInfo(tag, dict(attrs)))
        if tag == 'br':
            self._paragraphs.append([])

    def handle_endtag(self, tag):
        tag_info = self._tag_info_stack[-1]
        href = tag_info.attrs.get('href')
        last_paragraph = self._paragraphs[-1]
        last_segment = last_paragraph[-1] if last_paragraph else None
        if (self._preserve_urls and
                tag_info.name == 'a' and href and href != last_segment):
            self._append_segment('({href})'.format(href=href))

        if tag == 'p':
            self._paragraphs.append([])

        self._tag_info_stack.pop()

    def handle_data(self, data):
        data = ' '.join(data.split())
        if not self._is_in_body():
            return
        if data:
            self._append_segment(data)

    def handle_entityref(self, name):
        num = name2codepoint.get(name)
        if num is not None:
            self.handle_charref(num)

    def handle_charref(self, num):
        self._append_segment(chr(int(num)))

    def get_data(self):
        paragraph_texts = []
        for segments in self._paragraphs:
            paragraph_texts.append(' '.join(segments))
        return '\n'.join(paragraph_texts)

    def _is_in_body(self):
        if len(self._tag_info_stack) < 3:
            return False
        return (self._tag_info_stack[1].name == 'html' and
                self._tag_info_stack[2].name == 'body')

    def _append_segment(self, segment):
        self._paragraphs[-1].append(segment)
