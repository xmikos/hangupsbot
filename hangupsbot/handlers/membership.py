import hangups

from hangupsbot.utils import text_to_segments
from hangupsbot.handlers import handler


@handler.register(priority=5, event=hangups.MembershipChangeEvent)
def handle_membership_change(bot, event):
    """Handle conversation membership change"""
    # Test if watching for membership changes is enabled
    if not bot.get_config_suboption(event.conv_id, 'membership_watching_enabled'):
        return

    # Generate list of added or removed users
    event_users = [event.conv.get_user(user_id) for user_id
                   in event.conv_event.participant_ids]
    names = ', '.join([user.full_name for user in event_users])

    # JOIN
    if event.conv_event.type_ == hangups.MembershipChangeType.JOIN:
        # Test if user who added new participants is admin
        admins_list = bot.get_config_suboption(event.conv_id, 'admins')
        if event.user_id.chat_id in admins_list:
            yield from event.conv.send_message(
                text_to_segments(_('{}: Welcome!').format(names))
            )
        else:
            text = _(
                '**!!! WARNING !!!**\n'
                '{} invited user {} without authorization!\n'
                '\n'
                '{}: Please leave this conversation immediately!'
            ).format(event.user.full_name, names, names)
            bot.send_message(event.conv, text)
    # LEAVE
    else:
        bot.send_message(event.conv,
                         _('{} has jilted us :-( Hasta la vista, baby!').format(names))
