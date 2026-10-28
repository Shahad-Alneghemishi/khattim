from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("search/", views.search, name="search"),
    path("add/<int:rawg_id>/", views.add_game, name="add_game"),
]