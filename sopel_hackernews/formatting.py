"""sopel-hackernews formatting module

Part of sopel-hackernews, a Hacker News plugin for Sopel.
"""
from __future__ import annotations

from html import unescape
from html.parser import HTMLParser
import re

from sopel.formatting import CONTROL_ITALIC, CONTROL_MONOSPACE


CONSECUTIVE_SPACES_RE = re.compile(r' {2,}')


class HNParser(HTMLParser):
    """Custom HTML parser to convert HN's wacky HTML to IRC-formatted text."""

    def __init__(self):
        super().__init__()
        self.result = []
        self.single_newline_as_space = True

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            # note: HN doesn't close <p> tags
            # also note: HN doesn't put a <p> before the first paragraph
            self.result.append(' \N{RETURN SYMBOL} ')
        elif tag =='i':
            self.result.append(CONTROL_ITALIC)
        elif tag == 'pre':
            self.result.append(CONTROL_MONOSPACE)
            self.single_newline_as_space = False
        # ignore other tags, e.g. <a> just wraps plaintext URLs so handle_data()
        # will deal with those just fine

    def handle_endtag(self, tag):
        if tag == 'i':
            self.result.append(CONTROL_ITALIC)
        elif tag == 'pre':
            self.result.append(CONTROL_MONOSPACE)
            self.single_newline_as_space = True

    def handle_data(self, data):
        if self.single_newline_as_space:
            data = data.replace('\n', ' ')
        else:
            data = data.replace('\n', ' \N{RETURN SYMBOL} \n')
        self.result.extend(data.splitlines())

    def get_data(self):
        """Get the parsed data as a single string."""
        out = ''.join(self.result)
        out = unescape(out).replace('\n', ' \N{RETURN SYMBOL} ')
        return CONSECUTIVE_SPACES_RE.sub(' ', out)
