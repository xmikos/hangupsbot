import os, io

import hangups
from hangups import http_utils

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

    forward_to_list = bot.get_config_suboption(event.conv_id, 'forward_to')
    if forward_to_list:
        # Prepare attachments
        image_id_list = []
        for link in event.conv_event.attachments:
            # Download image
            try:
                res = yield from http_utils.fetch('get', link)
            except hangups.NetworkError as e:
                print('Failed to download image: {}'.format(e))
                continue
            # Upload image and get image_id
            try:
                image_id = yield from bot._client.upload_image(io.BytesIO(res.body),
                                                               filename=os.path.basename(link))
                image_id_list.append(image_id)
            except hangups.NetworkError as e:
                print('Failed to upload image: {}'.format(e))
                continue

        # Forward message to all destinations
        for dst in forward_to_list:
            try:
                conv = bot._conv_list.get(dst)
            except KeyError:
                continue

            # Prepend forwarded message with name of sender
            link = 'https://plus.google.com/u/0/{}/about'.format(event.user_id.chat_id)
            segments = [hangups.ChatMessageSegment(event.user.full_name, hangups.SegmentType.LINK,
                                                   link_target=link, is_bold=True),
                        hangups.ChatMessageSegment(': ', is_bold=True)]

            # Copy original message segments
            segments.extend(event.conv_event.segments)

            # Send text message first (without attachments)
            yield from conv.send_message(segments)

            # If there are attachments, send them separately
            for image_id in image_id_list:
                yield from conv.send_message([], image_id=image_id)
