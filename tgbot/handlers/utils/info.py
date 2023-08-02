from functools import wraps
from typing import Dict, Callable

import telegram
from telegram import Update

from tgbot.main import bot


def send_typing_action(func: Callable):
    """Sends typing action while processing func command."""
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=telegram.ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func


def extract_user_data_from_update(update: Update) -> Dict:
    """ python-telegram-bot's Update instance --> User info """
    user = update.effective_user.to_dict()

    return dict(
        user_id=user["id"],
        is_blocked_bot=False,
        **{
            k: user[k]
            for k in ["username", "first_name", "last_name", "language_code"]
            if k in user and user[k] is not None
        },
    )


def extract_group_data_from_update(update: Update) -> Dict:
    """ python-telegram-bot's Update instance --> User info """
    group = update.effective_chat.to_dict()

    return dict(
        group_id=group["id"],
        **{
            k: group[k]
            for k in ["description", "title", "type"]
            if k in group and group[k] is not None
        },
    )
