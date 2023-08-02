from telegram import ParseMode, Update
from telegram.ext import CallbackContext
from users.models import Group, User
from .decorators import checking_all


@checking_all
def command_start(update: Update, context: CallbackContext, user: User, group: Group) -> None:
    update.message.reply_text(text=text,
                              reply_markup=make_keyboard_for_start_command())
