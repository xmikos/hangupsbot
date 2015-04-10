import hangups
from hangups.ui.utils import get_conv_name

from hangupsbot.utils import text_to_segments
from hangupsbot.commands import command


@command.register_unknown
def unknown_command(bot, event, *args):
    """Unknown command handler"""
    bot.send_message(event.conv,
                     _('{}: Unknown command!').format(event.user.full_name))


@command.register
def help(bot, event, cmd=None, *args):
    """Help me, Obi-Wan Kenobi. You're my only hope.
       Usage: /bot help [command]"""

    cmd = cmd if cmd else 'help'
    try:
        command_fn = command.commands[cmd]
    except KeyError:
        yield from command.unknown_command(bot, event)
        return

    segments = [hangups.ChatMessageSegment('{}:'.format(cmd), is_bold=True),
                hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK)]
    segments.extend(text_to_segments(_(command_fn.__doc__)))

    if cmd == 'help':
        segments.extend([hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                         hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                         hangups.ChatMessageSegment(_('Supported commands:'), is_bold=True),
                         hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                         hangups.ChatMessageSegment(', '.join(sorted(command.commands.keys())))])

    bot.send_message_segments(event.conv, segments)


@command.register
def ping(bot, event, *args):
    """Let's play ping pong!"""
    bot.send_message(event.conv, 'pong')


@command.register
def echo(bot, event, *args):
    """Monkey see, monkey do!
       Usage: /bot echo text"""
    bot.send_message(event.conv, ' '.join(args))


@command.register(admin=True)
def quit(bot, event, *args):
    """Oh my God! They killed Kenny! You bastards!"""
    print(_('HangupsBot killed by user {} from conversation {}').format(event.user.full_name,
                                                                        get_conv_name(event.conv, truncate=True)))
    yield from event.conv.send_message([
        hangups.ChatMessageSegment(_('Et tu, Brute?'))
    ])
    yield from bot._client.disconnect()
