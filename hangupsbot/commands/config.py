import json

from hangupsbot.utils import text_to_segments
from hangupsbot.commands import command


@command.register(admin=True)
def config(bot, event, cmd=None, *args):
    """Show or change bot configuration
       Usage: /bot config [get|set] [key] [subkey] [...] [value]"""

    if cmd == 'get' or cmd is None:
        config_args = list(args)
        value = bot.config.get_by_path(config_args) if config_args else dict(bot.config)
    elif cmd == 'set':
        config_args = list(args[:-1])
        if len(args) >= 2:
            bot.config.set_by_path(config_args, json.loads(args[-1]))
            bot.config.save()
            value = bot.config.get_by_path(config_args)
        else:
            yield from command.unknown_command(bot, event)
            return
    else:
        yield from command.unknown_command(bot, event)
        return

    if value is None:
        value = _('Key not found!')

    config_path = ' '.join(k for k in ['config'] + config_args)
    text = (
        '**{}:**\n'
        '{}'
    ).format(config_path, json.dumps(value, indent=2, sort_keys=True))
    yield from event.conv.send_message(text_to_segments(text))


@command.register(admin=True)
def config_reload(bot, event, *args):
    """Reload bot configuration from file"""
    bot.config.load()
    yield from event.conv.send_message(text_to_segments(_('Configuration reloaded')))
