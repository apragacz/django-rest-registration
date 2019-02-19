import re


def detect_indent_num(text, ignore_first_line=True):
    r"""
    >>> detect_indent_num("")
    0
    >>> detect_indent_num("\n    foo\n")
    4
    >>> detect_indent_num("\n    foo\n        bar")
    4
    >>> detect_indent_num("\n  foo\n  bar")
    2
    >>> detect_indent_num("baz\n    foo\n        bar")
    4
    >>> detect_indent_num("baz\n    foo\n        bar", ignore_first_line=False)
    0
    """
    min_indent_num = len(text)

    for i, line in enumerate(text.split('\n')):
        if ignore_first_line and i == 0:
            continue
        line = line.rstrip(' ')
        if not line:
            continue

        m = re.search('[^ ]', line)
        assert m is not None

        indent_num = m.span()[0]
        if min_indent_num > indent_num:
            min_indent_num = indent_num

    return min_indent_num


def deindent(text, indent_num, ignore_first_line=True):
    r"""
    >>> deindent("", 4)
    ''
    >>> deindent("\n    abc", 4)
    '\nabc'
    >>> deindent("    abc", 4, ignore_first_line=False)
    'abc'
    """
    result_lines = []
    for i, line in enumerate(text.split('\n')):
        if ignore_first_line and i == 0:
            result_lines.append(line)
        else:
            result_lines.append(line[indent_num:])
    return '\n'.join(result_lines)
