import json
import os
import datetime

_BASE = os.path.dirname(os.path.abspath(__file__))

def _ratings_file(username):
    return os.path.join(_BASE, f"ratings_{username}.json")

def load_ratings(username):
    f = _ratings_file(username)
    if os.path.exists(f):
        with open(f) as fp: return json.load(fp)
    return {}

def save_rating(username, song_name, rating: int):
    ratings = load_ratings(username)
    ratings[song_name] = {"rating": rating, "date": datetime.date.today().isoformat()}
    with open(_ratings_file(username), 'w') as f: json.dump(ratings, f)
    return {1:0, 2:1, 3:2, 4:5, 5:10}.get(rating, 0)

def get_rating(username, song_name):
    return load_ratings(username).get(song_name, {}).get("rating", 0)

def get_top_rated_songs(username, n=10):
    ratings = load_ratings(username)
    return [(s, r["rating"]) for s, r in sorted(ratings.items(), key=lambda x: x[1]["rating"], reverse=True)[:n]]

def get_rating_stats(username):
    ratings = load_ratings(username)
    if not ratings: return {"avg": 0, "total": 0, "distribution": {i:0 for i in range(1,6)}}
    values = [r["rating"] for r in ratings.values()]
    return {"avg": round(sum(values)/len(values), 1), "total": len(values),
            "distribution": {i: values.count(i) for i in range(1, 6)}}
