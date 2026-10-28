from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .forms import ProfileForm
from .models import Profile, UserGame
from .rawg import RawgUnavailable, import_game, search_games
# Create your views here.

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("profile")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})

@login_required
def profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "games/profile.html", {"form": form, "profile": profile})

@login_required
def search(request):
    query = request.GET.get("q", "").strip()
    results = []
    error = ""

    if query:
        try:
            results = search_games(query)
        except RawgUnavailable as e:
            error = str(e)

    return render(request, "games/search.html", {"query": query, "results": results, "error": error})

@login_required
@require_POST
def add_game(request, rawg_id):
    try:
        game = import_game(rawg_id)
    except RawgUnavailable:
        return redirect("search")

    UserGame.objects.get_or_create(user=request.user, game=game)
    return redirect("search")