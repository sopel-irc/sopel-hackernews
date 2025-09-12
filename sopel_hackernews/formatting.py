"""sopel-hackernews formatting module

Part of sopel-hackernews, a Hacker News plugin for Sopel.
"""
from __future__ import annotations

from html import unescape
from html.parser import HTMLParser

from sopel.formatting import CONTROL_ITALIC, CONTROL_MONOSPACE


class HNParser(HTMLParser):
    """Custom HTML parser to convert HN's wacky HTML to IRC-formatted text."""

    def __init__(self):
        super().__init__()
        self.result = []

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            # note: HN doesn't close <p> tags
            # also note: HN doesn't put a <p> before the first paragraph
            self.result.append(' \N{RETURN SYMBOL} ')
        elif tag =='i':
            self.result.append(CONTROL_ITALIC)
        elif tag == 'pre':
            self.result.append(CONTROL_MONOSPACE)
        # ignore other tags, e.g. <a> just wraps plaintext URLs so handle_data()
        # will deal with those just fine

    def handle_endtag(self, tag):
        if tag == 'i':
            self.result.append(CONTROL_ITALIC)
        elif tag == 'pre':
            self.result.append(CONTROL_MONOSPACE)

    def handle_data(self, data):
        data = data.replace('\n', ' \N{RETURN SYMBOL} \n')
        self.result.extend([line.lstrip() for line in data.splitlines()])

    def get_data(self):
        """Get the parsed data as a single string."""
        out = ''.join(self.result)
        out = unescape(out).replace('\n', ' \N{RETURN SYMBOL} ')
        return out
