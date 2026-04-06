import json
import os
import datetime

BADGES = {
    "🎵 First Beat":      {"desc": "Get your first recommendation",        "check": lambda s: s["total_sessions"] >= 1},
    "👍 Music Lover":     {"desc": "Like 5 songs",                          "check": lambda s: s["total_likes"] >= 5},
    "🔥 On Fire":         {"desc": "Like 20 songs",                         "check": lambda s: s["total_likes"] >= 20},
    "📅 3-Day Streak":    {"desc": "Use the app 3 days in a row",           "check": lambda s: s["streak"] >= 3},
    "📅 7-Day Streak":    {"desc": "Use the app 7 days in a row",           "check": lambda s: s["streak"] >= 7},
    "🎭 Mood Explorer":   {"desc": "Try all 4 moods",                       "check": lambda s: len(s["moods_tried"]) >= 4},
    "🎸 Genre Master":    {"desc": "Try all 5 genres",                      "check": lambda s: len(s["genres_tried"]) >= 5},
    "🚀 Power User":      {"desc": "Complete 25 sessions",                  "check": lambda s: s["total_sessions"] >= 25},
    "💯 Century":         {"desc": "Complete 100 sessions",                 "check": lambda s: s["total_sessions"] >= 100},
    "🧘 Chill Master":    {"desc": "Get 10 Relaxed recommendations",        "check": lambda s: s["mood_counts"].get("Relaxed", 0) >= 10},
    "📚 Focus Champion":  {"desc": "Get 10 Focus recommendations",          "check": lambda s: s["mood_counts"].get("Focus", 0) >= 10},
}

def _stats_file(username):
    return f"stats_{username}.json"

def load_stats(username):
    f = _stats_file(username)
    if os.path.exists(f):
        with open(f) as fp:
            return json.load(fp)
    return {
        "total_sessions": 0,
        "total_likes": 0,
        "total_skips": 0,
        "streak": 0,
        "last_active_date": None,
        "moods_tried": [],
        "genres_tried": [],
        "mood_counts": {},
        "earned_badges": [],
        "xp": 0,
    }

def save_stats(username, stats):
    with open(_stats_file(username), 'w') as f:
        json.dump(stats, f)

def update_stats(username, mood, genre, feedback):
    stats = load_stats(username)
    today = datetime.date.today().isoformat()

    # Streak logic
    if stats["last_active_date"] is None:
        stats["streak"] = 1
    elif stats["last_active_date"] == today:
        pass  # same day, no change
    elif stats["last_active_date"] == (datetime.date.today() - datetime.timedelta(days=1)).isoformat():
        stats["streak"] += 1
    else:
        stats["streak"] = 1
    stats["last_active_date"] = today

    # Counters
    stats["total_sessions"] += 1
    if feedback == "like":
        stats["total_likes"] += 1
        stats["xp"] += 10
    elif feedback == "listen":
        stats["xp"] += 2
    elif feedback == "skip":
        stats["total_skips"] += 1
        stats["xp"] = max(0, stats["xp"] - 2)

    if mood not in stats["moods_tried"]:
        stats["moods_tried"].append(mood)
    if genre not in stats["genres_tried"]:
        stats["genres_tried"].append(genre)

    stats["mood_counts"][mood] = stats["mood_counts"].get(mood, 0) + 1

    # Check new badges
    newly_earned = []
    for badge, info in BADGES.items():
        if badge not in stats["earned_badges"] and info["check"](stats):
            stats["earned_badges"].append(badge)
            newly_earned.append(badge)

    save_stats(username, stats)
    return stats, newly_earned

def get_level(xp):
    levels = [
        (0,    "🌱 Newbie"),
        (50,   "🎧 Listener"),
        (150,  "🎵 Music Fan"),
        (300,  "🎤 Enthusiast"),
        (600,  "🌟 Audiophile"),
        (1000, "🏆 Legend"),
    ]
    level_name = levels[0][1]
    for threshold, name in levels:
        if xp >= threshold:
            level_name = name
    return level_name
