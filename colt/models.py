from multiprocessing.managers import BaseManager
from django.db import models
from utils.models import CreateUpdateTracker, nb, CreateTracker, GetOrNoneManager
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User, Group
# Create your models here.


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

    @classmethod
    def get_open_games(cls, group: Group) -> BaseManager:
        return Game.objects.filter(
            group=group, status__in=[
                Game.GameStatus.Playing, Game.GameStatus.Started
            ]
        )


class Section(CreateUpdateTracker):
    class SectionStatus(models.TextChoices):
        Playing = "Playing"
        Cancelled = "Cancelled"
        Finished = "Finished"

    status = models.CharField(max_length=32, default=SectionStatus.Playing)
    players = models.ManyToManyField(User, related_name="sections")
    played_players = models.ManyToManyField(
        User, related_name="played_sections"
    )
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name="sections"
    )
    bullet = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5),
        ],
        editable=False
    )
    current_magazine = models.PositiveBigIntegerField(
        default=0,
        help_text="this is the magazine we want to shoot.",
        **nb,
    )
