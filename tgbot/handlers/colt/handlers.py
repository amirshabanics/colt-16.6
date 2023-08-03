from telegram import ParseMode, Update
from telegram.ext import CallbackContext
from users.models import Group, User
from .decorators import checking_all
from colt.models import Game, Section


@checking_all(has_game=False, only_admin=True)
def command_play(update: Update, context: CallbackContext, user: User, group: Group,  **kwargs) -> None:
    game = Game.objects.create(group=group)
    message = update.message.reply_text(
        text="Create New Game. insert /join to join the game. shot shot!"
    )

    game.message_id = message.message_id
    game.save()


@checking_all(has_game=True, only_admin=True, update_players=True, game_status=[Game.GameStatus.Playing])
def command_skip(update: Update, context: CallbackContext, user: User, group: Group,  **kwargs) -> None:
    game: Game = kwargs.get("game")
    section = game.current_section
    section.skip_player()


@checking_all(has_game=True, only_admin=True, update_players=True, game_status=[Game.GameStatus.Playing])
def command_next(update: Update, context: CallbackContext, user: User, group: Group,  **kwargs) -> None:
    game: Game = kwargs.get("game")
    section = game.current_section
    section.play_turn(update, context)


@checking_all(has_game=True, game_status=[Game.GameStatus.Started], update_players=True, only_admin=True)
def command_start(update: Update, context: CallbackContext, user: User, group: Group,  **kwargs) -> None:
    game: Game = kwargs.get("game")
    if len(game.players.all()) <= 1:
        update.message.reply_text(
            text="Players are not enough.!"
        )
        return
    game.status = Game.GameStatus.Playing
    game.save()
    message = update.message.reply_text(
        text="Game started.!"
    )

    game.message_id = message.message_id
    game.save()

    Section.create_section(game=game, players=list(game.players.all()))


@checking_all(has_game=True, game_status=[Game.GameStatus.Started, Game.GameStatus.Playing], update_players=True)
def command_stat(update: Update, context: CallbackContext, user: User, group: Group,  **kwargs) -> None:
    pass


@checking_all(has_game=True, only_admin=True)
def command_cancel(update: Update, context: CallbackContext, user: User, group: Group,  **kwargs) -> None:
    opened_games = Game.get_open_games(group)
    opened_games.update(status=Game.GameStatus.Cancelled)
    Section.objects.filter(
        game__in=list(opened_games),
        status=Section.SectionStatus.Playing
    ).update(
        status=Section.SectionStatus.Cancelled
    )
    update.message.reply_text(
        text="Cancelled successfully!"
    )


@checking_all(has_game=True, game_status=[Game.GameStatus.Started], update_players=True)
def command_leave(update: Update, context: CallbackContext, user: User, group: Group,  **kwargs) -> None:

    game: Game = kwargs.get("game")
    if not game.players.filter(user_id=user.user_id).exists():
        update.message.reply_text(
            text="You didn't join the game before."
        )
        return

    game.players.remove(user)
    update.message.reply_text(
        text="You have leaved the game successfully!"
    )


@checking_all(has_game=True, game_status=[Game.GameStatus.Started], update_players=True)
def command_join(update: Update, context: CallbackContext, user: User, group: Group, **kwargs) -> None:
    game = kwargs.get("game")

    if game.players.filter(user_id=user.user_id).exists():
        update.message.reply_text(
            text="You joined the game before."
        )
        return

    game.players.add(user)
    update.message.reply_text(
        text="You have joined the game successfully!"
    )


@checking_all(has_game=True, game_status=[Game.GameStatus.Playing], update_players=True)
def command_shoot(update: Update, context: CallbackContext, user: User, group: Group, **kwargs) -> None:
    game: Game = kwargs.get("game")
    section = game.current_section
    _, current_player = section.player_turn
    if current_player != user:
        update.message.reply_text(
            text="It's not your turn."
        )
        return

    section.play_turn(update, context)
