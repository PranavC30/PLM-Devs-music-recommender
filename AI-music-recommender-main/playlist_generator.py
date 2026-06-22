import pandas as pd
import os

ENERGY_DURATION = {"Low": 4.5, "Medium": 3.8, "High": 3.2}
DEFAULT_DURATION = 4.0

def _load_df():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "songs.csv")
    return pd.read_csv(path)

def generate_playlist(mood, language, duration_minutes, genre=None, energy=None, avoid_songs=None):
    df = _load_df()
    avoid_songs = avoid_songs or []
    pool = df.copy()
    if mood:     pool = pool[pool["Mood"] == mood]
    if language: pool = pool[pool["Language"].str.lower() == language.lower()]
    if genre:    pool = pool[pool["Genre"] == genre]
    if energy:   pool = pool[pool["Energy"] == energy]
    if len(pool) < 3: pool = df[(df["Mood"] == mood) & (df["Language"].str.lower() == language.lower())]
    if len(pool) < 3: pool = df[df["Mood"] == mood]
    if len(pool) == 0: pool = df
    if avoid_songs: pool = pool[~pool["Song"].isin(avoid_songs)]
    if pool.empty: pool = _load_df()
    pool = pool.sample(frac=1).reset_index(drop=True)
    playlist, total_mins = [], 0.0
    for _, row in pool.iterrows():
        est = ENERGY_DURATION.get(str(row.get("Energy", "")).strip(), DEFAULT_DURATION)
        if total_mins + est > duration_minutes + DEFAULT_DURATION: break
        song = row.to_dict(); song["est_duration_min"] = est
        playlist.append(song); total_mins += est
        if total_mins >= duration_minutes: break
    return playlist, round(total_mins, 1)

def get_preset_playlists():
    return [
        {"name": "☀️ Morning Boost",     "mood": "Happy",   "language": "Hindi",   "duration": 20, "energy": "High"},
        {"name": "📚 Study Session",      "mood": "Focus",   "language": "Hindi",   "duration": 60, "energy": "Low"},
        {"name": "🏋️ Workout Mix",        "mood": "Happy",   "language": "English", "duration": 45, "energy": "High"},
        {"name": "🌙 Sleep Wind-Down",    "mood": "Relaxed", "language": "Hindi",   "duration": 30, "energy": "Low"},
        {"name": "💔 Heartbreak Therapy", "mood": "Sad",     "language": "Hindi",   "duration": 25, "energy": "Low"},
        {"name": "🎉 Party Starter",      "mood": "Happy",   "language": "Punjabi", "duration": 40, "energy": "High"},
        {"name": "🧘 Evening Chill",      "mood": "Relaxed", "language": "Hindi",   "duration": 30, "energy": "Low"},
        {"name": "🎯 Deep Focus Lo-fi",   "mood": "Focus",   "language": "English", "duration": 90, "genre": "Lo-fi"},
    ]
