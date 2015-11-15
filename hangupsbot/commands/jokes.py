import asyncio, random

from hangups import hangouts_pb2

from hangupsbot.utils import strip_quotes, text_to_segments
from hangupsbot.commands import command


@asyncio.coroutine
def easteregg_combo(client, conv_id, easteregg, eggcount=1, period=0.5):
    """Send easter egg combo (ponies, pitchforks, bikeshed, shydino)"""
    for i in range(eggcount):
        req = hangouts_pb2.EasterEggRequest(
            request_header=client.get_request_header(),
            conversation_id=hangouts_pb2.ConversationId(id=conv_id),
            easter_egg=hangouts_pb2.EasterEgg(message=easteregg)
        )
        res = yield from client.easter_egg(req)
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
    link = 'https://plus.google.com/u/0/{}/about'.format(event.user.id_.chat_id)
    text = _(
        '**!!! WARNING !!!**\n'
        'Agent {} ({}) has been reported to Niantic for attempted spoofing!'
    ).format(event.user.full_name, link)
    yield from event.conv.send_message(text_to_segments(text))
