from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages

from .forms import ProfileForm, RecommendForm
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
            return redirect("library")
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

TIME_RULES = {
    "short": (1, 10),
    "medium": (5, 30),
    "long": (15, None),
}

MOOD_GENRES = {
    "relax": {"Casual", "Puzzle", "Simulation", "Family"},
    "story": {"Adventure", "RPG"},
    "challenge": {"Platformer", "Strategy", "Fighting", "Shooter"},
    "action": {"Action", "Shooter", "Arcade", "Racing"},
}

def recommend_games(user, session_length, mood, limit=3):
    entries = UserGame.objects.filter(
        user=user,
        status__in=[UserGame.Status.BACKLOG, UserGame.Status.PLAYING]
    ).select_related("game")

    low, high = TIME_RULES[session_length]
    mood_genres = MOOD_GENRES[mood]
    picks = []

    for  entry in entries:
        game = entry.game
        score = 0
        reasons = []

        matched = mood_genres & set(game.genres)
        if matched:
            score += 3 * len(matched)
            reasons.append(f"Matches your mood ({', '.join(sorted(matched))})")

        if game.playtime and low <= game.playtime and (high is None or game.playtime <= high):
            score += 2
            reasons.append(f"Fits your time (about {game.playtime}h to beat)")

        if entry.status == UserGame.Status.PLAYING:
            score += 2
            reasons.append("You already started it")

        if score > 0:
            picks.append({"entry": entry, "score": score, "reasons": reasons})

    picks.sort(key=lambda p: (-p["score"], p["entry"].added_at))
    return picks[:limit]

@login_required
def recommend(request):
    form = RecommendForm(request.GET or None)
    picks = None
    if form.is_valid():
        picks = recommend_games(
            request.user,
            form.cleaned_data["session_length"],
            form.cleaned_data["mood"]
        )
    return render(request, "games/recommend.html", {"form": form, "picks": picks})

@login_required
def random_game(request):
    entries = UserGame.objects.filter(
        user=request.user,
        status__in=[UserGame.Status.BACKLOG, UserGame.Status.PLAYING],
    ).select_related("game")
    

    skip_id = request.GET.get("skip_id", "")
    candidates = entries.exclude(pk=skip_id) if skip_id.isdigit() else entries

    entry = candidates.order_by("?").first() or entries.first()
    return render(request, "games/random_game.html", {"entry": entry})
