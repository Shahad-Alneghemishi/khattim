from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages

from .forms import ProfileForm
from .models import Profile, UserGame
from .rawg import RawgUnavailable, import_game, search_games
# Create your views here.
def home(request):
    return render(request, "games/home.html")

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
        messages.error(request, "Could not add the game right now. Try again later.")
        return redirect("search")

    _, created = UserGame.objects.get_or_create(user=request.user, game=game)
    if created:
        messages.success(request, f"{game.name} was added to your library.")
    else:
        messages.info(request, f"{game.name} is already in your library.")
    return redirect("search")

@login_required
def library(request):
    status = request.GET.get("status", "")
    entries = (
        UserGame.objects.filter(user=request.user)
        .select_related("game")
        .order_by("-added_at")
    )
    if status in UserGame.Status.values:
        entries = entries.filter(status=status)

    return render(
        request,
        "games/library.html",
        {"entries": entries, "statuses": UserGame.Status.choices, "current_status": status}
    )

@login_required
@require_POST
def update_status(request, pk):
    entry = get_object_or_404(UserGame, pk=pk, user=request.user)
    new_status = request.POST.get("status")

    if new_status in UserGame.Status.values:
        entry.status = new_status
        entry.save()
        messages.success(request, f"{entry.game.name} status updated.")
    return redirect("library")

@login_required
@require_POST
def remove_game(request, pk):
    entry = get_object_or_404(UserGame, pk=pk, user=request.user)
    name = entry.game.name
    entry.delete()
    messages.success(request, f"{name} was removed from your library.")
    return redirect("library")