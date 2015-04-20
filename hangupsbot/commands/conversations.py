import itertools

from hangups.ui.utils import get_conv_name

from hangupsbot.utils import strip_quotes, text_to_segments
from hangupsbot.commands import command


def get_unique_users(bot, user_list):
    """Return list of unique chat_ids from list of user names"""
    users = itertools.chain.from_iterable(bot.find_users(strip_quotes(u)) for u in user_list)
    unique_users = list({u.id_.chat_id for u in users})
    return unique_users


@command.register(admin=True)
def conv_refresh(bot, event, conv_name, *args):
    """Create new conversation with same users as in old one except kicked users (use . for current conversation)
       Usage: /bot conv_refresh conversation_name [kicked_user_name_1] [kicked_user_name_2] [...]"""
    conv_name = strip_quotes(conv_name)
    convs = [event.conv] if conv_name == '.' else bot.find_conversations(conv_name)
    kicked_chat_ids = get_unique_users(bot, args)

    for c in convs:
        old_chat_ids = {u.id_.chat_id for u in bot.find_users('', conv=c)}
        new_chat_ids = list(old_chat_ids - set(kicked_chat_ids))

        # Create new conversation
        res = yield from bot._client.createconversation(new_chat_ids, force_group=True)
        conv_id = res['conversation']['id']['id']
        yield from bot._client.setchatname(conv_id, c.name)
        yield from bot._conv_list.get(conv_id).send_message(
            text_to_segments(_('**Welcome!**\n'
                               'This is new refreshed conversation. Old conversation has been '
                               'terminated, but you are one of the lucky ones who survived cleansing! '
                               'If you are still in old conversation, please leave it.'))
        )

        # Destroy old one and leave it
        yield from bot._client.setchatname(c.id_, _('[TERMINATED] {}').format(c.name))
        yield from c.send_message(
            text_to_segments(_('**!!! WARNING !!!**\n'
                               'This conversation has been terminated! Please leave immediately!'))
        )
        yield from bot._conv_list.leave_conversation(c.id_)


@command.register(admin=True)
def conv_create(bot, event, conv_name, *args):
    """Create new conversation and invite users to it
       Usage: /bot conv_create conversation_name [user_name_1] [user_name_2] [...]"""
    conv_name = strip_quotes(conv_name)
    chat_id_list = get_unique_users(bot, args)
    if not chat_id_list:
        yield from command.unknown_command(bot, event)
        return

    res = yield from bot._client.createconversation(chat_id_list, force_group=True)
    conv_id = res['conversation']['id']['id']
    yield from bot._client.setchatname(conv_id, conv_name)
    yield from bot._conv_list.get(conv_id).send_message(text_to_segments(_('Welcome!')))


@command.register(admin=True)
def conv_add(bot, event, conv_name, *args):
    """Invite users to existing conversation (use . for current conversation)
       Usage: /bot conv_add conversation_name [user_name_1] [user_name_2] [...]"""
    conv_name = strip_quotes(conv_name)
    chat_id_list = get_unique_users(bot, args)
    if not chat_id_list:
        yield from command.unknown_command(bot, event)
        return

    convs = [event.conv] if conv_name == '.' else bot.find_conversations(conv_name)
    for c in convs:
        yield from bot._client.adduser(c.id_, chat_id_list)


@command.register(admin=True)
def conv_rename(bot, event, conv_name, *args):
    """Rename conversation (use . for current conversation)
       Usage: /bot conv_rename conversation_name new_conversation_name"""
    conv_name = strip_quotes(conv_name)
    new_conv_name = strip_quotes(' '.join(args))

    convs = [event.conv] if conv_name == '.' else bot.find_conversations(conv_name)
    for c in convs:
        yield from bot._client.setchatname(c.id_, new_conv_name)


@command.register(admin=True)
def conv_send(bot, event, conv_name, *args):
    """Send message to conversation as bot (use . for current conversation)
       Usage: /bot conv_send conversation_name text"""
    conv_name = strip_quotes(conv_name)

    convs = [event.conv] if conv_name == '.' else bot.find_conversations(conv_name)
    for c in convs:
        yield from c.send_message(text_to_segments(' '.join(args)))


@command.register(admin=True)
def conv_leave(bot, event, conv_name='', *args):
    """Leave current (or specified) conversation
       Usage: /bot conv_leave [conversation_name]"""
    conv_name = strip_quotes(conv_name)

    convs = [event.conv] if not conv_name or conv_name == '.' else bot.find_conversations(conv_name)
    for c in convs:
        yield from c.send_message(text_to_segments(_('I\'ll be back!')))
        yield from bot._conv_list.leave_conversation(c.id_)


@command.register(admin=True)
def conv_list(bot, event, conv_name='', *args):
    """List all conversations where bot is wreaking havoc
       Usage: /bot conv_list [conversation_name]
       Legend: c ... commands, f ... forwarding, a ... autoreplies"""
    conv_name = strip_quotes(conv_name)

    convs = bot.list_conversations() if not conv_name else bot.find_conversations(conv_name)
    convs_text = []
    for c in convs:
        s = '{} [c: {:d}, f: {:d}, a: {:d}]'.format(
            get_conv_name(c, truncate=True),
            bot.get_config_suboption(c.id_, 'commands_enabled'),
            bot.get_config_suboption(c.id_, 'forwarding_enabled'),
            bot.get_config_suboption(c.id_, 'autoreplies_enabled')
        )
        convs_text.append(s)

    text = _('**Active conversations:**\n'
             '{}').format('\n'.join(convs_text))
    yield from event.conv.send_message(text_to_segments(text))
