from django.db import models
from django.conf import settings
# Create your models here.

class Game(models.Model):
    rawg_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)
    image = models.URLField(blank=True)
    genres = models.JSONField(default=list)
    playtime = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class UserGame(models.Model):
    class Status(models.TextChoices):
        BACKLOG = "backlog", "Backlog"
        PLAYING = "playing", "Playing"
        FINISHED = "finished", "Finished"
        DROPPED = "dropped", "Dropped"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.BACKLOG
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "game")

    def __str__(self):
        return f"{self.user} - {self.game} ({self.status})"

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True)

    def __str__(self):
        return f"Profile of {self.user}"
