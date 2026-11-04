from django.urls import path

from . import views

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("search/", views.search, name="search"),
    path("add/<int:rawg_id>/", views.add_game, name="add_game"),
    path("library/", views.library, name="library"),
    path("library/<int:pk>/status/", views.update_status, name="update_status"),
    path("library/<int:pk>/remove/", views.remove_game, name="remove_game"),
    path("recommend/", views.recommend, name="recommend"),
    path("random/", views.random_game, name="random_game"),
    path("theme/", views.toggle_theme, name="toggle_theme"),
]