import hangups

from hangupsbot.utils import text_to_segments
from hangupsbot.handlers import handler


@handler.register(priority=7, event=hangups.ChatMessageEvent)
def handle_forward(bot, event):
    """Handle message forwarding"""
    # Test if message is not empty
    if not event.text:
        return

    # Test if message forwarding is enabled
    if not bot.get_config_suboption(event.conv_id, 'forwarding_enabled'):
        return

    # Test if there are actually any forwarding destinations
    forward_to_list = bot.get_config_suboption(event.conv_id, 'forward_to')
    if not forward_to_list:
        return

    # Prepare attachments
    image_id_list = yield from bot.upload_images(event.conv_event.attachments)

    # Forward message to all destinations
    for dst in forward_to_list:
        try:
            conv = bot._conv_list.get(dst)
        except KeyError:
            continue

        # Prepend forwarded message with name of sender
        link = 'https://plus.google.com/u/0/{}/about'.format(event.user_id.chat_id)
        segments = text_to_segments('**[{}]({}):** '.format(event.user.full_name, link))

        # Copy original message segments
        segments.extend(event.conv_event.segments)

        # Send text message first (without attachments)
        yield from conv.send_message(segments)

        # If there are attachments, send them separately
        for image_id in image_id_list:
            yield from conv.send_message([], image_id=image_id)
