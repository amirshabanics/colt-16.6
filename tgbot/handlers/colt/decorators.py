from telegram import ParseMode, Update
from telegram.ext import CallbackContext
from users.models import Group, User
from colt.models import Game, Section
from .messages import player_list_message


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
                    text="Please first join me to a group.",)
                return

            user = User.get_user(update, context)

            if only_admin is True and not user.is_admin:
                update.message.reply_text(
                    text="Permission Denied",)
                return

            if only_admin is False and user.is_admin:
                update.message.reply_text(
                    text="Permission Denied.",)
                return

            opened_games = Game.get_open_games(group)
            has_opened_game = opened_games.exists()
            if has_game is True and not has_opened_game:
                update.message.reply_text(
                    text="Not Found Any Game.",)
                return

            if has_game is False and has_opened_game:
                update.message.reply_text(
                    text="Found A Game.",)
                return

            if game_status is not None and not has_opened_game:
                update.message.reply_text(
                    text="Not Found Any Game.",)
                return

            game: Game = opened_games.first()
            if game_status is not None:
                if game.status not in game_status:
                    update.message.reply_text(
                        text="You can not do this action in this state.",)
                    return

            func(update, context, user, group, game=game)

            game = Game.get_open_games(group).first()
            if game is not None and update_players == True:
                update.message.reply_text(
                    text=player_list_message(
                        game
                    )
                )

        return wrapper

    return decorator
