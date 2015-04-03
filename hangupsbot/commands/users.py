import hangups
from hangups.ui.utils import get_conv_name

from hangupsbot.utils import strip_quotes
from hangupsbot.commands import command


@command.register(admin=True)
def user_list(bot, event, conv_name='', user_name='', *args):
    """List all participants in current (or specified) conversation
       You can also use . for current conversation. Includes G+ accounts and emails.
       Usage: /bot users_list [conversation_name] [user_name]"""
    conv_name = strip_quotes(conv_name)
    user_name = strip_quotes(user_name)
    convs = [event.conv] if not conv_name or conv_name == '.' else bot.find_conversations(conv_name)
    segments = []
    for c in convs:
        segments.append(hangups.ChatMessageSegment(_('List of participants in "{}" ({} total):').format(
                                                   get_conv_name(c, truncate=True), len(c.users)),
                                                   is_bold=True))
        segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))
        for u in bot.find_users(user_name, conv=c):
            link = 'https://plus.google.com/u/0/{}/about'.format(u.id_.chat_id)
            segments.append(hangups.ChatMessageSegment(u.full_name, hangups.SegmentType.LINK,
                                                       link_target=link))
            if u.emails:
                segments.append(hangups.ChatMessageSegment(' ('))
                segments.append(hangups.ChatMessageSegment(u.emails[0], hangups.SegmentType.LINK,
                                                           link_target='mailto:{}'.format(u.emails[0])))
                segments.append(hangups.ChatMessageSegment(')'))
            segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))
        segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))
    bot.send_message_segments(event.conv, segments)


@command.register(admin=True)
def user_find(bot, event, user_name='', *args):
    """Find users known to bot by their name
       Usage: /bot users_find [user_name]"""
    user_name = strip_quotes(user_name)
    segments = [hangups.ChatMessageSegment(_('Search results for user name "{}":').format(user_name),
                                           is_bold=True),
                hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK)]
    for u in bot.find_users(user_name):
        link = 'https://plus.google.com/u/0/{}/about'.format(u.id_.chat_id)
        segments.append(hangups.ChatMessageSegment(u.full_name, hangups.SegmentType.LINK,
                                                   link_target=link))
        if u.emails:
            segments.append(hangups.ChatMessageSegment(' ('))
            segments.append(hangups.ChatMessageSegment(u.emails[0], hangups.SegmentType.LINK,
                                                       link_target='mailto:{}'.format(u.emails[0])))
            segments.append(hangups.ChatMessageSegment(')'))
        segments.append(hangups.ChatMessageSegment(' ... {}'.format(u.id_.chat_id)))
        segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))
    bot.send_message_segments(event.conv, segments)
