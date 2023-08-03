from multiprocessing.managers import BaseManager
from django.db import models
from utils.models import CreateUpdateTracker, nb, CreateTracker, GetOrNoneManager
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User, Group
import random
from telegram import Update
from telegram.ext import CallbackContext
from tgbot.handlers.colt.statics import (
    NOT_BE_KILLED,
    BE_KILLED,
    END_GAME,
)
from .utils import random_item
# Create your models here.


class PlayerOrder(models.Model):
    order = models.PositiveIntegerField(null=False, blank=False)
    player = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('player', 'order',)

    def __str__(self):
        return f"{self.order}: {self.player.tg_str}"


class Game(CreateUpdateTracker):
    class GameStatus(models.TextChoices):
        Playing = "Playing"
        Cancelled = "Cancelled"
        Started = "Started"
        Finished = "Finished"

    status = models.CharField(
        max_length=32, default=GameStatus.Started, **nb
    )
    players = models.ManyToManyField(User, related_name="games")
    message_id = models.PositiveBigIntegerField(**nb)
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, null=False, blank=False, related_name="games"
    )
    winner = models.ForeignKey(
        User, related_name="winner_games", on_delete=models.SET_NULL, **nb)

    @classmethod
    def get_open_games(cls, group: Group) -> BaseManager:
        return Game.objects.filter(
            group=group, status__in=[
                Game.GameStatus.Playing, Game.GameStatus.Started
            ]
        )

    @property
    def current_section(self) -> "Section":
        return self.sections.filter(status=Section.SectionStatus.Playing).first()


class Section(CreateUpdateTracker):
    class SectionStatus(models.TextChoices):
        Playing = "Playing"
        Cancelled = "Cancelled"
        Finished = "Finished"

    status = models.CharField(max_length=32, default=SectionStatus.Playing)
    players = models.ManyToManyField(PlayerOrder, related_name="sections")
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name="sections"
    )
    bullet = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5),
        ],
    )
    current_magazine = models.PositiveBigIntegerField(
        default=0,
        help_text="this is the magazine we want to shoot.",
        **nb,
    )

    def skip_player(self):
        self.bullet = (self.bullet + 1) % 6
        self.current_magazine = (self.current_magazine + 1) % 6
        self.save()

    @classmethod
    def create_section(cls, game: Game, players: list[User], shuffle: bool = True):
        section = Section.objects.create(
            game=game,
            bullet=random.randint(0, 5),
        )

        section_players = [*list(players)]
        if shuffle:
            random.shuffle(section_players)
        section_order_players = []
        for i, p in enumerate(section_players):
            player_order, _ = PlayerOrder.objects.get_or_create(
                order=i, player=p
            )
            section_order_players.append(player_order)
        section.players.clear()
        section.players.add(*section_order_players)

    @property
    def all_players(self) -> list[User]:
        players = self.players.all().order_by("order")
        return list(map(lambda p: p.player, list(players)))

    @property
    def player_turn(self) -> tuple[int, User]:
        players = self.all_players
        player_index = self.current_magazine % len(players)
        player = players[player_index]
        return (player_index, player)

    def play_turn(self, update: Update, context: CallbackContext):
        players: list[User] = self.all_players
        player_index, _ = self.player_turn
        game = self.game
        if self.current_magazine == self.bullet:
            update.message.reply_text(
                text=random_item(BE_KILLED)
            )
            self.status = self.SectionStatus.Finished
            self.save()
            new_players = players[player_index + 1:] + players[:player_index]

            if len(new_players) == 1:
                game.winner = new_players[0]
                game.status = game.GameStatus.Finished
                game.save()
                update.message.reply_text(
                    text=random_item(END_GAME)
                )
                return

            Section.create_section(
                game=game,
                players=new_players,
                shuffle=False
            )

            return

        self.current_magazine = (self.current_magazine + 1) % 6
        self.save()
        update.message.reply_text(
            text=random_item(NOT_BE_KILLED)
        )
