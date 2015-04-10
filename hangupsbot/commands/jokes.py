import asyncio, random

import hangups

from hangupsbot.utils import strip_quotes
from hangupsbot.commands import command


@asyncio.coroutine
def easteregg_combo(client, conv_id, easteregg, eggcount=1, period=0.5):
    """Send easter egg combo (ponies, pitchforks, bikeshed, shydino)"""
    for i in range(eggcount):
        yield from client.sendeasteregg(conv_id, easteregg)
        if eggcount > 1:
            yield from asyncio.sleep(period + random.uniform(-0.1, 0.1))


@command.register(admin=True)
def easteregg(bot, event, easteregg, eggcount=1, period=0.5, conv_name='', *args):
    """Annoy people with easter egg combo in current (or specified) conversation!
       Usage: /bot easteregg easter_egg_type [count] [period] [conv_name]
       Supported easter eggs: ponies, pitchforks, bikeshed, shydino"""
    conv_name = strip_quotes(conv_name)
    convs = [event.conv] if not conv_name or conv_name == '.' else bot.find_conversations(conv_name)
    for c in convs:
        asyncio.async(
            easteregg_combo(bot._client, c.id_, easteregg, int(eggcount), float(period))
        ).add_done_callback(lambda future: future.result())


@command.register
def spoof(bot, event, *args):
    """Spoof IngressBot on specified GPS coordinates
       Usage: /bot spoof latitude,longitude [hack|fire|deploy|mod] [level] [count]"""
    segments = [hangups.ChatMessageSegment(_('!!! WARNING !!!'), is_bold=True),
                hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK)]
    segments.append(hangups.ChatMessageSegment(_('Agent {} (').format(event.user.full_name)))
    link = 'https://plus.google.com/u/0/{}/about'.format(event.user.id_.chat_id)
    segments.append(hangups.ChatMessageSegment(link, hangups.SegmentType.LINK,
                                               link_target=link))
    segments.append(hangups.ChatMessageSegment(_(') has been reported to Niantic for attempted spoofing!')))
    bot.send_message_segments(event.conv, segments)
