import itertools

from hangups import hangouts_pb2
from hangups.hangouts_pb2 import InviteeID
from hangups.ui.utils import get_conv_name

from hangupsbot.utils import strip_quotes, text_to_segments
from hangupsbot.commands import command


def get_unique_users(bot, user_list):
    """Return list of unique chat_ids from list of user names"""
    users = itertools.chain.from_iterable(bot.find_users(strip_quotes(u)) for u in user_list)
    unique_users = list({u.id_.chat_id for u in users})
    return unique_users


def get_unique_user_objects(bot, user_list):
    """Return list of unique user objects from list of user names"""
    return itertools.chain.from_iterable(bot.find_users(strip_quotes(u)) for u in user_list)


@command.register(admin=True)
def conv_refresh(bot, event, conv_name, *args):
    """Create new conversation with same users as in old one except kicked users (use . for current conversation)
       Usage: /bot conv_refresh conversation_name [kicked_user_name_1] [kicked_user_name_2] [...]"""
    conv_name = strip_quotes(conv_name)
    convs = [event.conv] if conv_name == '.' else bot.find_conversations(conv_name)
    kicked_chat_ids = get_unique_users(bot, args)

    for c in convs:
        new_chat_ids = {u for u in bot.find_users('', conv=c) if u.id_.chat_id not in set(kicked_chat_ids)}
        invitee_ids = [InviteeID(
            gaia_id=u.id_.gaia_id,
            fallback_name=u.full_name
        ) for u in new_chat_ids]
        # Create new conversation

        request = hangouts_pb2.CreateConversationRequest(
            request_header=bot._client.get_request_header(),
            type=hangouts_pb2.CONVERSATION_TYPE_GROUP,
            client_generated_id=bot._client.get_client_generated_id(),
            name=c.name,
            invitee_id=invitee_ids
        )
        res = yield from bot._client.create_conversation(request)
        conv_id = res.conversation.conversation_id.id
        bot._conv_list.add_conversation(res.conversation)
        conv = bot._conv_list.get(conv_id)

        yield from conv.rename(c.name)
        yield from conv.send_message(
            text_to_segments(('**Welcome!**\n'
                              'This is the new refreshed conversation. Old conversation has been '
                              'terminated, but you are one of the lucky ones who survived cleansing! '
                              'If you are still in old conversation, please leave it.'))
        )

        # Destroy old one and leave it
        yield from c.rename(('[TERMINATED] {}').format(c.name))
        yield from c.send_message(
            text_to_segments(('**!!! WARNING !!!**\n'
                              'This conversation has been terminated! Please leave immediately!'))
        )
        yield from c.leave()


@command.register(admin=True)
def conv_create(bot, event, conv_name, *args):
    """Create new conversation and invite users to it
       Usage: /bot conv_create conversation_name [user_name_1] [user_name_2] [...]"""
    conv_name = strip_quotes(conv_name)
    unique_user_objects = get_unique_user_objects(bot, args)
    if not unique_user_objects:
        yield from command.unknown_command(bot, event)
        return
    invitee_ids = [InviteeID(
        gaia_id=u.id_.gaia_id,
        fallback_name=u.full_name
    ) for u in unique_user_objects]
    request = hangouts_pb2.CreateConversationRequest(
        request_header=bot._client.get_request_header(),
        type=hangouts_pb2.CONVERSATION_TYPE_GROUP,
        client_generated_id=bot._client.get_client_generated_id(),
        name=conv_name,
        invitee_id=invitee_ids
    )
    res = yield from bot._client.create_conversation(request)
    conv = bot._conv_list.add_conversation(res.conversation)
    yield from conv.rename(conv_name)
    yield from conv.send_message(text_to_segments(('Welcome!')))


@command.register(admin=True)
def conv_add(bot, event, conv_name, *args):
    """Invite users to existing conversation (use . for current conversation)
       Usage: /bot conv_add conversation_name [user_name_1] [user_name_2] [...]"""
    conv_name = strip_quotes(conv_name)
    unique_user_objects = get_unique_user_objects(bot, args)
    if not unique_user_objects:
        yield from command.unknown_command(bot, event)
        return
    invitee_ids = [InviteeID(
        gaia_id=u.id_.gaia_id,
        fallback_name=u.full_name
    ) for u in unique_user_objects]
    convs = [event.conv] if conv_name == '.' else bot.find_conversations(conv_name)
    for c in convs:
        req = hangouts_pb2.AddUserRequest(
            request_header=bot._client.get_request_header(),
            invitee_id=invitee_ids,
            event_request_header=c._get_event_request_header()
        )
        res = yield from bot._client.add_user(req)
        c.add_event(res.created_event)


@command.register(admin=True)
def conv_rename(bot, event, conv_name, *args):
    """Rename conversation (use . for current conversation)
       Usage: /bot conv_rename conversation_name new_conversation_name"""
    conv_name = strip_quotes(conv_name)
    new_conv_name = strip_quotes(' '.join(args))

    convs = [event.conv] if conv_name == '.' else bot.find_conversations(conv_name)
    for c in convs:
        yield from c.rename(new_conv_name)


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
        yield from c.leave()


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
