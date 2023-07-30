# coding=utf8
"""sopel-hackernews

Hacker News plugin for Sopel.
"""
from __future__ import unicode_literals, absolute_import, division, print_function

import html
from urllib.parse import urlparse

import requests

from sopel import plugin


HN_PATTERN = 'https?:\/\/news\.ycombinator\.com\/item\?id=(?P<ID>\d+)'
PLUGIN_PREFIX = '[Hacker News] '


def clean_hn_text(text):
    """Deal with HN weirdness like <p> for line breaks, HTML entities, etc."""
    return html.unescape(text.replace('<p>', ' \N{RETURN SYMBOL} '))


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

    results = requests.get("https://hn.algolia.com/api/v1/search?query={}".format(query)).json()

    try:
        item = results['hits'][0]

        # TODO: timestamp
        bot.say(
            'Story: ' + item['title'],
            truncation = '…',
            trailing = ' | ▲ {score} | 🗨️ {comments} | {hn_link}'.format(
                score = item['points'],
                comments = item['num_comments'],
                hn_link = 'https://news.ycombinator.com/item?id=' + item['objectID'],
            )
        )
    except:
        bot.say("No HN discussion found")


@plugin.url(HN_PATTERN)
@plugin.output_prefix(PLUGIN_PREFIX)
def forward_hn(bot, trigger):
    item = requests.get(
        'https://hacker-news.firebaseio.com/v0/item/{}.json'.format(trigger.group('ID'))
    ).json()

    if item is None:
        bot.say("No HN item found.")
        return

    # TODO: timestamps
    if item['type'] == 'comment':
        bot.say(
            'Comment by {author}: {text}'.format(
                author = item['by'],
                text = clean_hn_text(item['text']),
            ),
            truncation = ' […]',
        )
    else:
        domain = urlparse(item['url']).hostname

        bot.say(
            'Story: {title}{dead} | ▲ {score} | 🗨️ {comments} | {url}'.format(
                title = item['title'],
                dead = ' [DEAD]' if item.get('dead') else '',
                score = item['score'],
                comments = item['descendants'],
                url = item['url'],
            ),
            truncation = ' ' + domain,
        )
