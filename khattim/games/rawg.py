import requests
import hashlib
from django.core.cache import cache
from django.conf import settings

from .models import Game

BASE_URL = "https://api.rawg.io/api"

class RawgUnavailable(Exception):
    pass

def _get(path, **params):
    if not settings.RAWG_API_KEY:
        raise RawgUnavailable("RAWG API key is not set.")
    try:
        response = requests.get(
            f"{BASE_URL}{path}",
            params={"key": settings.RAWG_API_KEY, **params},
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
    except(requests.RequestException, ValueError):
        raise RawgUnavailable("Could not reach RAWG right now.")

def search_games(query):
    key = "rawg_search:" + hashlib.md5(query.strip().lower().encode()).hexdigest()
    results = cache.get(key)
    if results is None:
        results = _get("/games", search=query, page_size=10)["results"]
        cache.set(key, results, 60 * 60)
    return results

def import_game(rawg_id):
    game = Game.objects.filter(rawg_id=rawg_id).first()
    if game:
        return game

    data = _get(f"/games/{rawg_id}")
    game, _ = Game.objects.get_or_create(
        rawg_id=data["id"],
        defaults={
            "name": data["name"],
            "image": data.get("background_image") or "",
            "genres": [g["name"] for g in data.get("genres", [])],
            "playtime": data.get("playtime") or 0,
        },
    )
    return game