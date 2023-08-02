"""
    Telegram event handlers.py
"""
from telegram.ext import (
    Dispatcher, Filters,
    CommandHandler, MessageHandler,
    CallbackQueryHandler,
)

from dtb.settings import DEBUG
from tgbot.handlers.broadcast_message.manage_data import CONFIRM_DECLINE_BROADCAST
from tgbot.handlers.broadcast_message.static_text import broadcast_command
from tgbot.handlers.onboarding.manage_data import SECRET_LEVEL_BUTTON
from tgbot.handlers.vpn.manage_data import (
    BUY_BUTTON,
    EDU_BUTTON,
    LINK_LIST_BUTTON,
    CANCEL_BUTTON,
    HISTORY_BUTTON,
)
from tgbot.handlers.utils import files, error
from tgbot.handlers.admin import handlers as admin_handlers
from tgbot.handlers.location import handlers as location_handlers
from tgbot.handlers.broadcast_message import handlers as broadcast_handlers
from tgbot.handlers.colt import handlers as colt_handlers
from tgbot.main import bot


def setup_dispatcher(dp):
    """
    Adding handlers.py for events from Telegram
    """

    dp.add_handler(CommandHandler("start", colt_handlers.command_start))
    # dp.add_handler(MessageHandler(Filters.all, onboarding_start_handlers.command_start))

    return dp


n_workers = 0 if DEBUG else 4
dispatcher = setup_dispatcher(Dispatcher(bot, update_queue=None, workers=n_workers, use_context=True))
