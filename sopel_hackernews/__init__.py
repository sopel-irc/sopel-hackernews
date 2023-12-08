# coding=utf8
"""sopel-hackernews

Hacker News plugin for Sopel.
"""
from __future__ import unicode_literals, absolute_import, division, print_function

from datetime import datetime
import html
from urllib.parse import urlparse

import pytz
import requests

from sopel import plugin
from sopel.config import types
from sopel.tools import time


HN_PATTERN = 'https?:\/\/news\.ycombinator\.com\/item\?id=(?P<ID>\d+)'
PLUGIN_PREFIX = '[Hacker News] '


class HackerNewsSection(types.StaticSection):
    relative_timestamps = types.BooleanAttribute('relative_timestamps', default=True)


def setup(bot):
    bot.settings.define_section('hackernews', HackerNewsSection)


def clean_hn_text(text):
    """Deal with HN weirdness like <p> for line breaks, HTML entities, etc."""
    return html.unescape(text.replace('<p>', ' \N{RETURN SYMBOL} '))


def get_formatted_timestamp(ts, channel, bot):
    """Get formatted timestamp based on the channel and the bot's settings."""
    ts = datetime.fromtimestamp(ts, tz=pytz.utc)

    if bot.settings.hackernews.relative_timestamps:
        now = datetime.now(tz=pytz.utc)
        return time.seconds_to_human(now - ts)

    zone = time.get_timezone(
        db=bot.db,
        config=bot.settings,
        channel=channel,
    )
    return time.format_time(
        db=bot.db,
        config=bot.settings,
        zone=zone,
        channel=channel,
        time=ts,
    )


@plugin.commands('reversehn', 'rhn')
@plugin.output_prefix(PLUGIN_PREFIX)
def reverse_hn(bot, trigger):
    if trigger.group(2):
        query = trigger.group(2)
    else:
        if trigger.sender not in bot.memory['last_seen_url']:
            bot.reply("I haven't seen any links recently.")
            return

        query = bot.memory['last_seen_url'][trigger.sender]

    results = requests.get('https://hn.algolia.com/api/v1/search?query={}'.format(query)).json()

    try:
        item = results['hits'][0]

        bot.say(
            'Story: ' + item['title'],
            truncation='…',
            trailing=' | ▲ {score} | 🗨️ {comments} | {when} | {hn_link}'.format(
                score=item['points'],
                comments=item['num_comments'],
                when=get_formatted_timestamp(item['created_at_i'], trigger.sender, bot),
                hn_link='https://news.ycombinator.com/item?id=' + item['objectID'],
            )
        )
    except (IndexError, KeyError, TypeError):
        bot.say('No HN discussion found for that link.')


@plugin.url(HN_PATTERN)
@plugin.output_prefix(PLUGIN_PREFIX)
def forward_hn(bot, trigger):
    item = requests.get(
        'https://hacker-news.firebaseio.com/v0/item/{}.json'.format(trigger.group('ID'))
    ).json()

    if item is None:
        bot.say('Item {} not found.'.format(trigger.group('ID')))
        return

    if item.get('deleted'):
        bot.say('Item {} is a deleted {}.'.format(item['id'], item['type']))
        return

    if item['type'] == 'comment':
        bot.say(
            'Comment{dead} by {author} ({when}): {text}'.format(
                dead=' [DEAD]' if item.get('dead', False) else '',
                author=item['by'],
                when=get_formatted_timestamp(item['time'], trigger.sender, bot),
                text=clean_hn_text(item['text']),
            ),
            truncation=' […]',
        )
    elif item['type'] == 'story':
        url = item.get('url')

        bot.say(
            'Story: {title}{dead} | 👤 {author} | 📆 {when} | ▲ {score} | 🗨️ {comments}{url}'.format(
                title=item['title'],
                dead=' [DEAD]' if item.get('dead', False) else '',
                author=item.get('by') or '(nobody)',
                when=get_formatted_timestamp(item['time'], trigger.sender, bot),
                score=item['score'],
                comments=item['descendants'],
                url=(' | ' + url) if url else '',
            ),
            truncation=(' ' + urlparse(url).hostname) if url else ' …',
        )
    elif item['type'] == 'job':
        url = item.get('url')

        bot.say(
            'Job: {title} | 👤 {author} | 📆 {when}{url}'.format(
                title=item['title'],
                author=item.get('by') or '(nobody)',
                when=get_formatted_timestamp(item['time'], trigger.sender, bot),
                url=(' | ' + url) if url else '',
            ),
            truncation=(' ' + urlparse(url).hostname) if url else ' …',
        )
