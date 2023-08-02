from telegram import ParseMode, Update
from telegram.ext import CallbackContext
from users.models import Group, User
from .decorators import checking_all
from colt.models import Game


@checking_all
def command_start(update: Update, context: CallbackContext, user: User, group: Group) -> None:
    # def command_start(update: Update, context: CallbackContext) -> None:
    # todo only admin user of group
    if Game.get_open_games(group).exists():
        update.message.reply_text(
            text="You have created a game before. Please if you want to play another game cancel your last game first."
        )
        return
    game = Game.objects.create(group=group)
    message = update.message.reply_text(
        text="Game started. insert /join to join the game. shot shot!"
    )

    game.message_id = message.message_id
    game.save()


@checking_all
def command_cancel(update: Update, context: CallbackContext, user: User, group: Group) -> None:
    # def command_start(update: Update, context: CallbackContext) -> None:
    Game.get_open_games(group).update(status=Game.GameStatus.Cancelled)
    # todo only admin user of group
    update.message.reply_text(
        text="Cancelled successfully!"
    )


@checking_all
def command_join(update: Update, context: CallbackContext, user: User, group: Group) -> None:
    # def command_start(update: Update, context: CallbackContext) -> None:
    opened_games = Game.get_open_games(group)
    if not opened_games.exist():
        update.message.reply_text(
            text="Not found any game."
        )
        return
    # todo only simple user

    game: Game = opened_games.first()
    if game.status != Game.GameStatus.Started:
        update.message.reply_text(
            text="You can't join to a started game."
        )
        return
    if game.players.filter(user_id=user.user_id).exists():
        update.message.reply_text(
            text="You joined the game before."
        )
        return

    # # todo dynamic it
    # if len(game.players.all()) >= 6:
    #     update.message.reply_text(
    #         text="Fully player!"
    #     )
    #     return
    game.players.add(user)
    update.message.reply_text(
        text="You have joined the game successfully!"
    )
