import re

import hangups

from hangupsbot.utils import word_in_text
from hangupsbot.handlers import handler


@handler.register(priority=7, event=hangups.ChatMessageEvent)
def handle_autoreply(bot, event):
    """Handle autoreplies to keywords in messages"""
    # Test if message is not empty
    if not event.text:
        return

    # Test if autoreplies are enabled
    if not bot.get_config_suboption(event.conv_id, 'autoreplies_enabled'):
        return

    autoreplies_list = bot.get_config_suboption(event.conv_id, 'autoreplies')
    if autoreplies_list:
        for kwds, sentence in autoreplies_list:
            reply = False
            for kw in kwds:
                if kw == "*":
                    reply = True
                    break
                elif kw.lower().startswith("regex:") and re.search(kw[6:], event.text,
                                                                   re.DOTALL | re.IGNORECASE):
                    reply = True
                    break
                elif word_in_text(kw, event.text):
                    reply = True
                    break
            if reply:
                bot.send_message(event.conv, sentence)

