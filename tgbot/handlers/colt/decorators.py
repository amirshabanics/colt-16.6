from telegram import ParseMode, Update
from telegram.ext import CallbackContext
from users.models import Group, User
from colt.models import Game, Section
from .messages import player_list_message
from .statics import (
    ADMIN_ONLY,
    GROUP_ONLY,
    HAS_GAME_ONLY,
    HAS_NOT_GAME_ONLY,
    SPECIFIC_STATUS_ONLY,
)


def checking_all(
    only_admin: bool = None,
        has_game: bool = None,
        game_status: list[Game.GameStatus] = None,
        update_players: bool = False,
) -> None:
    def decorator(func):
        def wrapper(update: Update, context: CallbackContext) -> None:
            group = Group.get_if_is_group(update, context)
            game = None
            if group is None:
                update.message.reply_text(
                    text=GROUP_ONLY,
                )
                return

            user = User.get_user(update, context)

            if only_admin is True and not user.is_admin:
                update.message.reply_text(
                    text=ADMIN_ONLY
                )
                return

            if only_admin is False and user.is_admin:
                update.message.reply_text(
                    text="Permission Denied!"
                )
                return

            opened_games = Game.get_open_games(group)
            has_opened_game = opened_games.exists()
            if has_game is True and not has_opened_game:
                update.message.reply_text(
                    text=HAS_GAME_ONLY
                )
                return

            if has_game is False and has_opened_game:
                update.message.reply_text(
                    text=HAS_NOT_GAME_ONLY,
                )
                return

            if game_status is not None and not has_opened_game:
                update.message.reply_text(
                    text=HAS_GAME_ONLY
                )
                return

            game: Game = opened_games.first()
            if game_status is not None:
                if game.status not in game_status:
                    update.message.reply_text(
                        text=SPECIFIC_STATUS_ONLY
                    )
                    return

            func(update, context, user, group, game=game)

            if game is not None and update_players == True:
                context.bot.send_message(
                    text=player_list_message(
                        game
                    ),
                    parse_mode="Markdown",
                    chat_id=group.group_id
                )

        return wrapper

    return decorator
