from collections import deque
from html.parser import HTMLParser
from typing import Dict, List, Optional, Tuple


def convert_html_to_text_preserving_urls(value: str) -> str:
    return convert_html_to_text(value, preserve_urls=True)


def convert_html_to_text(value: str, preserve_urls: bool = False) -> str:
    stripper = MLStripper(preserve_urls=preserve_urls)
    stripper.feed(value)
    stripper.close()
    return stripper.get_data()


class MLStripper(HTMLParser):

    def __init__(self, preserve_urls: bool = False) -> None:
        super().__init__(convert_charrefs=True)
        self.reset()
        self._paragraphs = [[]]  # type: List[List[str]]
        self._tag_info_stack = deque([TagInfo(None, {})])
        self._preserve_urls = preserve_urls

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        self._tag_info_stack.append(TagInfo(tag, dict(attrs)))
        if tag == 'br':
            self._paragraphs.append([])

    def handle_endtag(self, tag: str) -> None:
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

    def handle_data(self, data: str) -> None:
        data = ' '.join(data.split())
        if not self._is_in_body():
            return
        if data:
            self._append_segment(data)

    def error(self, message: str) -> None:
        raise ValueError("HTML parse error: {message}".format(
            message=message))

    def get_data(self) -> str:
        paragraph_texts = []
        for segments in self._paragraphs:
            paragraph_texts.append(' '.join(segments))
        return '\n'.join(paragraph_texts)

    def _is_in_body(self) -> bool:
        if len(self._tag_info_stack) < 3:
            return False
        return (self._tag_info_stack[1].name == 'html' and
                self._tag_info_stack[2].name == 'body')

    def _append_segment(self, segment: str) -> None:
        self._paragraphs[-1].append(segment)


class TagInfo:

    def __init__(self, name: Optional[str], attrs: Dict[str, Optional[str]]) -> None:
        super().__init__()
        self._name = name
        self._attrs = attrs

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def attrs(self) -> Dict[str, Optional[str]]:
        return self._attrs
