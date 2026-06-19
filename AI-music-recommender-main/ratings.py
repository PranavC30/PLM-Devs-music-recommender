import json
import os
import datetime

def _ratings_file(username):
    return os.path.join(os.path.dirname(__file__), f"ratings_{username}.json")

def load_ratings(username):
    f = _ratings_file(username)
    if os.path.exists(f):
        with open(f) as fp:
            return json.load(fp)
    return {}  # { "Song Name": {"rating": 4, "date": "2024-01-01"} }

def save_rating(username, song_name, rating: int):
    """Save a 1-5 star rating for a song. Returns XP earned."""
    ratings = load_ratings(username)
    ratings[song_name] = {
        "rating": rating,
        "date": datetime.date.today().isoformat()
    }
    with open(_ratings_file(username), 'w') as f:
        json.dump(ratings, f)
    # XP mapping: 1★=0, 2★=1, 3★=2, 4★=5, 5★=10
    xp_map = {1: 0, 2: 1, 3: 2, 4: 5, 5: 10}
    return xp_map.get(rating, 0)

def get_rating(username, song_name):
    """Returns the stored rating (int 1-5) or 0 if not rated."""
    ratings = load_ratings(username)
    return ratings.get(song_name, {}).get("rating", 0)

def get_top_rated_songs(username, n=10):
    """Returns top-n songs sorted by rating desc."""
    ratings = load_ratings(username)
    sorted_songs = sorted(ratings.items(), key=lambda x: x[1]["rating"], reverse=True)
    return [(s, r["rating"]) for s, r in sorted_songs[:n]]

def get_rating_stats(username):
    """Returns dict with avg rating, total rated, distribution."""
    ratings = load_ratings(username)
    if not ratings:
        return {"avg": 0, "total": 0, "distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}}
    values = [r["rating"] for r in ratings.values()]
    distribution = {i: values.count(i) for i in range(1, 6)}
    return {
        "avg": round(sum(values) / len(values), 1),
        "total": len(values),
        "distribution": distribution
    }
