import os, glob, asyncio


class CommandDispatcher(object):
    """Register commands and run them"""
    def __init__(self):
        self.commands = {}
        self.unknown_command = None

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

    def register(self, func):
        """Decorator for registering command"""
        # Automatically wrap command function in coroutine
        func = asyncio.coroutine(func)

        self.commands[func.__name__] = func
        return func

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
