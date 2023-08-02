from telegram import ParseMode, Update
from telegram.ext import CallbackContext
from users.models import Group, User


def checking_all(func) -> None:
    def wrapper(update: Update, context: CallbackContext) -> None:
        group = Group.get_if_is_group(update, context)
        if group is None:
            update.message.reply_text(text="Please first join me to a group.",)
            return

        user = User.get_user(update, context)

        func(update, context, user, group)
        # func(update, context)

    return wrapper
