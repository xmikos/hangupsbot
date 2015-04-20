from hangups.ui.utils import get_conv_name

from hangupsbot.utils import strip_quotes, text_to_segments
from hangupsbot.commands import command


def user_to_text(user):
    """Return text representation of user"""
    link = 'https://plus.google.com/u/0/{}/about'.format(user.id_.chat_id)
    text = ['[{}]({})'.format(user.full_name, link)]
    if user.emails:
        text.append(' ([{}](mailto:{}))'.format(user.emails[0], user.emails[0]))
    text.append(' ... id:{}'.format(user.id_.chat_id))
    return ''.join(text)


@command.register(admin=True)
def user_list(bot, event, conv_name='', user_name='', *args):
    """List all participants in current (or specified) conversation
       You can also use . for current conversation. Includes G+ accounts and emails.
       Usage: /bot user_list [conversation_name] [user_name]"""
    conv_name = strip_quotes(conv_name)
    user_name = strip_quotes(user_name)
    convs = [event.conv] if not conv_name or conv_name == '.' else bot.find_conversations(conv_name)
    text = []
    for c in convs:
        text.append(_(
            '**List of participants in "{}" ({} total):**'
        ).format(get_conv_name(c, truncate=True), len(c.users)))
        for u in bot.find_users(user_name, conv=c):
            text.append(user_to_text(u))
        text.append('')
    yield from event.conv.send_message(text_to_segments('\n'.join(text)))


@command.register(admin=True)
def user_find(bot, event, user_name='', *args):
    """Find users known to bot by their name
       Usage: /bot user_find [user_name]"""
    user_name = strip_quotes(user_name)
    text = [_('**Search results for user name "{}":**').format(user_name)]
    for u in bot.find_users(user_name):
        text.append(user_to_text(u))
    yield from event.conv.send_message(text_to_segments('\n'.join(text)))
