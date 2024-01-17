# sopel-hackernews

Hacker News plugin for Sopel.

## Development status

The current version is more or less stable, but is still considered beta or
pre-1.0 due to missing planned features and lack of testing for edge cases. See
plans for 1.0 at https://github.com/sopel-irc/sopel-hackernews/issues/3

We welcome contributions from anyone who feels like implementing something from
the 1.0 "wishlist", as well as bug reports and feature suggestions.

## Installing

Releases are hosted on PyPI, so after installing Sopel, all you need is `pip`:

```shell
$ pip install sopel-hackernews
```

## Usage

Links to Hacker News items are expanded automatically.

You can search for a link on HN using the `.rhn` command:

```
.rhn https://somecool.site/that/posted/an/article/
```

## Credits

Loosely based on [dasu's `hn.py` module](https://github.com/dasu/syrup-sopel-modules/blob/8f644ba4b4cdda06200f18a36959796ae7979fb6/hn.py),
which was licensed as "literally do whatever you want, i'm not liable for
anything lol". Thank you for the springboard!
