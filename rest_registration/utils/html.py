from collections import deque, namedtuple
from html.parser import HTMLParser


def convert_html_to_text_preserving_urls(value):
    return convert_html_to_text(value, preserve_urls=True)


def convert_html_to_text(value, preserve_urls=False):
    stripper = MLStripper(preserve_urls=preserve_urls)
    stripper.feed(value)
    stripper.close()
    return stripper.get_data()


TagInfo = namedtuple('TagInfo', ('name', 'attrs'))


class MLStripper(HTMLParser):

    def __init__(self, preserve_urls=False):
        super().__init__(convert_charrefs=True)
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

    def error(self, message):
        raise ValueError("HTML parse error: {message}".format(
            message=message))

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
