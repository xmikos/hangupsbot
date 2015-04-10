import os, glob, asyncio


class CommandDispatcher:
    """Register commands and run them"""
    def __init__(self):
        self.commands = {}
        self.commands_admin = []
        self.unknown_command = None

    def get_admin_commands(self, bot, conv_id):
        """Get list of admin-only commands (set by plugins or in config.json)"""
        commands_admin = bot.get_config_suboption(conv_id, 'commands_admin') or []
        return list(set(commands_admin + self.commands_admin))

    @asyncio.coroutine
    def run(self, bot, event, *args, **kwds):
        """Run command"""
        try:
            func = self.commands[args[0]]
        except KeyError:
            if self.unknown_command:
                func = self.unknown_command
            else:
                raise

        args = list(args[1:])

        try:
            yield from func(bot, event, *args, **kwds)
        except Exception as e:
            print(e)

    def register(self, *args, admin=False):
        """Decorator for registering command"""
        def wrapper(func):
            # Automatically wrap command function in coroutine
            func = asyncio.coroutine(func)
            self.commands[func.__name__] = func
            if admin:
                self.commands_admin.append(func.__name__)
            return func

        # If there is one (and only one) positional argument and this argument is callable,
        # assume it is the decorator (without any optional keyword arguments)
        if len(args) == 1 and callable(args[0]):
            return wrapper(args[0])
        else:
            return wrapper

    def register_unknown(self, func):
        """Decorator for registering unknown command"""
        # Automatically wrap command function in coroutine
        func = asyncio.coroutine(func)
        self.unknown_command = func
        return func


# Create CommandDispatcher singleton
command = CommandDispatcher()

# Build list of commands
_plugins = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
__all__ = [os.path.splitext(os.path.basename(f))[0] for f in _plugins
           if os.path.isfile(f) and not os.path.basename(f).startswith("_")]

# Load all commands
from hangupsbot.commands import *
