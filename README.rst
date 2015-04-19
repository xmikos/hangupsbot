HangupsBot
==========

Bot for Google Hangouts

Requirements
------------

- Python >= 3.3
- hangups (https://github.com/tdryer/hangups)
- ReParser (https://github.com/xmikos/reparser)
- appdirs (https://github.com/ActiveState/appdirs)
- asyncio (https://pypi.python.org/pypi/asyncio) for Python < 3.4

Usage
-----

Run ``hangupsbot --help`` to see all available options.
Start HangupsBot by running ``hangupsbot``.

You can configure basic settings in ``config.json`` file. This file will be
copied to user data directory (e.g. ``~/.local/share/hangupsbot/`` on Linux)
after first start of HangupsBot.

The first time you start HangupsBot, you will be prompted to log into your
Google account. Your credentials will only be sent to Google, and only
session cookies will be stored locally. If you have trouble logging in,
try logging in through a browser first.

Help
----
::

    usage: hangupsbot [-h] [-d] [--log LOG] [--cookies COOKIES] [--config CONFIG] [--version]

    optional arguments:
      -h, --help         show this help message and exit
      -d, --debug        log detailed debugging messages (default: False)
      --log LOG          log file path (default:
                         ~/.local/share/hangupsbot/hangupsbot.log)
      --cookies COOKIES  cookie storage path (default:
                         ~/.local/share/hangupsbot/cookies.json)
      --config CONFIG    config storage path (default:
                         ~/.local/share/hangupsbot/config.json)
      --version          show program's version number and exit

Features (event handlers)
-------------------------

- **autoreplies** - automatically reply to specified keywords in messages
- **commands** - run ``/bot`` commands (type ``/bot help`` for list of available commands)
- **forwarding** - forward messages from one conversation to another
- **membership** - watch conversations for added/removed users
- **rename** - watch for renamed conversations (*only example plugin for now*)

Development
-----------

You can extend HangupsBot in two ways - by writing ``handlers`` or ``commands`` plugins.
Every Python file (which doesn't start with \_) in ``handlers`` and ``commands`` directories
is loaded automatically.

Handlers
^^^^^^^^

Functions in plugins can be registered as event handlers by decorating them with
``@handler.register(priority=10, event=None)`` decorator.

If *event* parameter is ``None`` (default), all event types are forwarded to handler.
If you want to handle only some specific type of event, you can set *event*
to ``hangups.ChatMessageEvent``, ``hangups.MembershipChangeEvent``
or ``hangups.RenameEvent``.

You can change priority of handler by specifying *priority* parameter (default is 10).
A lower number means higher priority. If you raise ``StopEventHandling`` exception in
your handler, current event will not be handled by any other handler.

Commands
^^^^^^^^

Functions in plugins can be registered as ``/bot`` commands by decorating them with
``@command.register(admin=False)`` decorator.

If *admin* parameter is ``False`` (default), anyone can run the command.
If *admin* is ``True``, only admins (as set in ``config.json``) can run it.

See existing commands for examples.
