from django.contrib import admin
from .models import Game, Profile, UserGame
# Register your models here.

admin.site.register(Game)
admin.site.register(UserGame)
admin.site.register(Profile)