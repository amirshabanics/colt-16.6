from telegram import ParseMode, Update
from telegram.ext import CallbackContext
from users.models import Group, User
from .decorators import checking_all
from colt.models import Game
from .messages import player_list_message


@checking_all
def command_play(update: Update, context: CallbackContext, user: User, group: Group) -> None:
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
def command_start(update: Update, context: CallbackContext, user: User, group: Group) -> None:
    # def command_start(update: Update, context: CallbackContext) -> None:
    # todo only admin user of group
    opened_games = Game.get_open_games(group)
    if not opened_games.exists():
        update.message.reply_text(
            text="Not found any game."
        )
        return
    game: Game = opened_games.first()
    game.status = Game.GameStatus.Playing
    game.save()
    message = update.message.reply_text(
        text="Game started. insert /join to join the game. shot shot!"
    )

    game.message_id = message.message_id
    game.save()


@checking_all
def command_cancel(update: Update, context: CallbackContext, user: User, group: Group) -> None:
    # def command_start(update: Update, context: CallbackContext) -> None:
    Game.get_open_games(group).update(status=Game.GameStatus.Cancelled)
    # todo cacel open sections
    # todo only admin user of group
    update.message.reply_text(
        text="Cancelled successfully!"
    )


@checking_all
def command_leave(update: Update, context: CallbackContext, user: User, group: Group) -> None:
    # def command_start(update: Update, context: CallbackContext) -> None:
    opened_games = Game.get_open_games(group)
    if not opened_games.exists():
        update.message.reply_text(
            text="Not found any game."
        )
        return
    # todo only simple user

    game: Game = opened_games.first()
    if game.status != Game.GameStatus.Started:
        update.message.reply_text(
            text="You can't leave from a started game."
        )
        return
    if not game.players.filter(user_id=user.user_id).exists():
        update.message.reply_text(
            text="You didn't join the game before."
        )
        return

    game.players.remove(user)
    update.message.reply_text(
        text="You have leaved the game successfully!"
    )
    context.bot.edit_message_text(chat_id=group.group_id, message_id=game.message_id,
                                  text=player_list_message(game.players.all()))
    update.message.reply_text(
        text=player_list_message(game.players.all())
    )


@checking_all
def command_join(update: Update, context: CallbackContext, user: User, group: Group) -> None:
    # def command_start(update: Update, context: CallbackContext) -> None:
    opened_games = Game.get_open_games(group)
    if not opened_games.exists():
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
    context.bot.edit_message_text(chat_id=group.group_id, message_id=game.message_id,
                                  text=player_list_message(game.players.all()))
    update.message.reply_text(
        text=player_list_message(game.players.all())
    )
